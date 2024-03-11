import numpy
import time
import math
import threading
import logging
import sys
import shutil
import os
import subprocess
import platform
import inspect
from ruamel.yaml import YAML
from pathlib import Path
from psutil import virtual_memory
from threading import Event, Thread
from multiprocessing.shared_memory import SharedMemory
from voxel.instruments.instrument import Instrument
from voxel.writers.data_structures.shared_double_buffer import SharedDoubleBuffer
from voxel.acquisition.base import BaseAcquisition
from voxel.processes.max_projection import MaxProjection

class ExASPIMAcquisition(BaseAcquisition):

    def __init__(self, instrument: Instrument, config_filename: str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # current working directory
        this_dir = Path(__file__).parent.resolve()
        self.config_path = this_dir / Path(config_filename)
        self.config = YAML().load(Path(self.config_path))
        self.acquisition = self.config['acquisition']
        self.instrument = instrument
        for operation_type, operation_dict in self.config['acquisition']['operations'].items():
            setattr(self, operation_type, dict())
            self._construct_operations(operation_type, operation_dict)
        self._verify_directories()
        self._verify_acquisition()

    def run(self):

        acquisition_threads = dict()
        transfer_threads = dict()
        filenames = dict()

        for tile in self.config['acquisition']['tiles']:

            # sanity check length of scan
            for writer_id, writer in self.writers.items():
                chunk_count_px = writer.chunk_count_px
                tile_count_px = tile['frame_count_px']
                if tile_count_px < chunk_count_px:
                    raise ValueError(f'tile frame count {tile_count_px} \
                        is less than chunk size = {writer.chunk_count_px} px')

            # move all tiling stages to correct positions
            for tiling_stage_id, tiling_stage in self.instrument.tiling_stages.items():
                # grab stage axis letter
                instrument_axis = tiling_stage.instrument_axis
                tile_position = tile['position_mm'][instrument_axis]
                self.log.info(f'moving stage {tiling_stage_id} to {instrument_axis} = {tile_position} mm')
                tiling_stage.move_absolute(tile_position)

            # wait on all stages... simultaneously
            for tiling_stage_id, tiling_stage in self.instrument.tiling_stages.items():
                while tiling_stage.is_axis_moving():
                    instrument_axis = tiling_stage.instrument_axis
                    tile_position = tile['position_mm'][instrument_axis]
                    self.log.info(f'waiting for stage {tiling_stage_id}: {instrument_axis} = {tiling_stage.position} -> {tile_position} mm')
                    time.sleep(0.01)

            # TODO WE NEED TO DO BELOW BY REFERENCING TO CHANNEL IN INSTRUMENT CLASS
            
            # move filter wheels to correct postions
            for filter_wheel_id, filter_wheel in self.instrument.filter_wheels.items():
                filter_wheel_id = filter_wheel.id
                filter_name = tile['filter'][filter_wheel_id]
                self.log.info(f'moving filter wheel {filter_wheel_id} to {filter_name}')
                filter_wheel.filter = filter_name

            # adjust lasers to correct powers
            for laser_id, laser in self.instrument.lasers.items():
                laser.power_setpoint_mw = tile['power_mw']

            # setup camera, data writing engines, and processes
            for camera_id, camera in self.instrument.cameras.items():

                # filename
                tile_num_x = tile['tile_number']['x']
                tile_num_y = tile['tile_number']['y']
                tile_num_z = tile['tile_number']['z']
                channel = tile['channel']
                filename_prefix = tile['prefix']
                filenames[camera_id] = f'{filename_prefix}_x_{tile_num_x:04}_y_{tile_num_y:04}_z_{tile_num_z:04}_ch_{channel}_cam_{camera_id}'

                # pass in camera specific camera, writer, and processes
                thread = threading.Thread(target=self.engine,
                    args=(tile, filenames[camera_id],
                            camera,
                            self.writers[camera_id],
                            self.processes[camera_id],
                            ))
                acquisition_threads[camera_id] = thread 

            # collect time sensitive hardware components
            for camera_id in acquisition_threads:
                acquisition_threads[camera_id].start()

            for camera_id in acquisition_threads:
                acquisition_threads[camera_id].join()

            # handle starting and waiting for file transfers
            if self.transfers:
                for transfer_id in list(transfer_threads.keys()):
                    transfer_thread = transfer_threads.pop(transfer_id)
                    if transfer_thread.is_alive():
                        self.log.info(f"waiting on file transfer for {transfer_id}")
                        transfer_thread.wait_until_finished()
                for camera_id, camera in self.instrument.cameras.items():
                    transfer_threads[camera_id] = self.transfers[camera_id]
                    transfer_threads[camera_id].local_directory = writer.path
                    transfer_threads[camera_id].filename = filenames[camera_id]
                    self.log.info(f"starting file transfer of for {camera_id}")
                    transfer_threads[camera_id].start()

        # wait for last tiles file transfer
        if self.transfers:
            for thread_id in list(transfer_threads.keys()):
                transfer_thread = transfer_threads.pop(thread_id)
                if transfer_thread.is_alive():
                    self.log.info(f"waiting on file transfer for {thread_id}")
                    transfer_thread.wait_until_finished()

    def engine(self, tile, filename, camera, writer, processes):

        # setup writer
        writer.row_count_px = camera.roi['height_px']
        writer.column_count_px = camera.roi['width_px']
        writer.frame_count_px = tile['frame_count_px']
        writer.x_pos_mm = tile['position_mm']['x']
        writer.y_pos_mm = tile['position_mm']['y']
        writer.z_pos_mm = tile['position_mm']['z']
        writer.x_voxel_size_um = tile['voxel_size_um']['x']
        writer.y_voxel_size_um = tile['voxel_size_um']['x']
        writer.z_voxel_size_um = tile['voxel_size_um']['x']
        writer.filename = filename
        writer.channel = tile['channel']

        chunk_size = writer.chunk_count_px
        chunk_lock = threading.Lock()
        img_buffer = SharedDoubleBuffer((chunk_size, camera.roi['height_px'], camera.roi['width_px']),
                                        dtype=writer.data_type)

        # setup processes
        process_buffers = list()
        process_images = list()
        for process in processes:
            process.row_count_px = camera.roi['height_px']
            process.column_count_px = camera.roi['width_px']
            process.frame_count_px = tile['frame_count_px']
            process.filename = filename
            img_bytes = numpy.prod(camera.roi['height_px']*camera.roi['width_px'])*numpy.dtype(process.data_type).itemsize
            buffer = SharedMemory(create=True, size=int(img_bytes))
            process_buffers.append(buffer)
            process.buffer_image = numpy.ndarray((camera.roi['height_px'], camera.roi['width_px']), dtype=process.data_type, buffer=buffer.buf)
            process.prepare(buffer.name)

        # set up writer and camera
        writer.prepare()
        camera.prepare()
        writer.start()
        camera.start()
        for process in processes:
            process.start()

        frame_index = 0
        chunk_count = math.ceil(tile['frame_count_px'] / chunk_size)
        remainder = tile['frame_count_px'] % chunk_size
        last_chunk_size = chunk_size if not remainder else remainder
        last_frame_index = tile['frame_count_px'] - 1

        # Images arrive serialized in repeating channel order.
        for stack_index in range(tile['frame_count_px']):
            chunk_index = stack_index % chunk_size
            # Start a batch of pulses to generate more frames and movements.
            if chunk_index == 0:
                chunks_filled = math.floor(stack_index / chunk_size)
                remaining_chunks = chunk_count - chunks_filled
            # Grab camera frame
            current_frame = camera.grab_frame()
            camera.signal_acquisition_state()
            img_buffer.add_image(current_frame)

            # Dispatch either a full chunk of frames or the last chunk,
            # which may not be a multiple of the chunk size.
            if chunk_index == chunk_size - 1 or stack_index == last_frame_index:
                while not writer.done_reading.is_set():
                    time.sleep(0.001)
                # Dispatch chunk to each StackWriter compression process.
                # Toggle double buffer to continue writing images.
                # To read the new data, the StackWriter needs the name of
                # the current read memory location and a trigger to start.
                # Lock out the buffer before toggling it such that we
                # don't provide an image from a place that hasn't been
                # written yet.
                with chunk_lock:
                    img_buffer.toggle_buffers()
                    if writer.path is not None:
                        writer.shm_name = \
                            img_buffer.read_buf_mem_name
                        writer.done_reading.clear()

            # max projection test
            for process in processes:
                while process.new_image.is_set():
                    time.sleep(0.1)
                process.buffer_image[:,:] = current_frame
                process.new_image.set()

            frame_index += 1
            
        writer.wait_to_finish()
        for process in processes:
            process.wait_to_finish()
            # process.close()
        camera.stop()

        # clean up the image buffer
        self.log.debug(f"deallocating shared double buffer.")
        img_buffer.close_and_unlink()
        del img_buffer
        for buffer in process_buffers:
            buffer.close()
            buffer.unlink()
            del buffer