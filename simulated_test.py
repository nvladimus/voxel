import numpy
import time
import math
import threading
import logging
import sys
from pathlib import Path
from spim_core.config_base import Config
from threading import Event, Thread
from instrument import Instrument
from writers.data_structures.shared_double_buffer import SharedDoubleBuffer
from multiprocessing.shared_memory import SharedMemory
from writers.imaris import Writer

if __name__ == '__main__':

    # Setup logging.
    # Create log handlers to dispatch:
    # - User-specified level and above to print to console if specified.
    logger = logging.getLogger()  # get the root logger.
    # Remove any handlers already attached to the root logger.
    logging.getLogger().handlers.clear()
    # logger level must be set to the lowest level of any handler.
    logger.setLevel(logging.DEBUG)
    fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s'
    datefmt = '%Y-%m-%d,%H:%M:%S'
    log_formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel('INFO')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)

    # instrument
    instrument = Instrument('simulated_instrument.yaml')
    instrument.construct()

    # acquisition
    this_dir = Path(__file__).parent.resolve()
    config_path = this_dir / Path('test_acquisition.yaml')
    config = Config(str(config_path))
    acquisition = config.cfg['acquisition']

    # storage
    storage = acquisition['storage']
    filename_prefix = storage['filename_prefix']
    local_drive = storage['local_drive']
    external_drive = storage['external_drive']

    # transfer
    transfer = acquisition['transfer']
    protocol = transfer['protocol']
    flags = transfer['flags']

    for tile in acquisition['tiles']:

        # filename
        tile_num_x = tile['tile_number']['x']
        tile_num_y = tile['tile_number']['y']
        tile_num_z = tile['tile_number']['z']
        channel = tile['channel']

        # stages
        x_position_mm = tile['position_mm']['x']
        y_position_mm = tile['position_mm']['y']
        z_position_mm = tile['position_mm']['z']
        instrument.tiling_stages['ASI MS-8000 x axis']['object'].move_absolute(x_position_mm)
        instrument.tiling_stages['ASI MS-8000 y axis']['object'].move_absolute(y_position_mm)
        instrument.tiling_stages['ASI MS-8000 z axis']['object'].move_absolute(z_position_mm)

        # filter wheel
        filter_name = tile['filter']
        instrument.filter_wheels['ASI FW-1000']['object'].set_filter(filter_name)

        # laser
        laser_power = tile['power_mw']

        # writer
        stack_writer_workers = dict()
        chunk_lock = dict()
        img_buffer = dict()

        for camera_id in instrument.cameras:
            filename = f'{filename_prefix}_x_{tile_num_x:04}_y_{tile_num_y:04}_z_{tile_num_z:04}_ch_{channel}_cam_{camera_id}.ims'
            row_count = instrument.cameras[camera_id]['object'].roi['height_px']
            column_count = instrument.cameras[camera_id]['object'].roi['width_px']
            stack_writer_workers[camera_id] = instrument.cameras[camera_id]['writer']['object']
            stack_writer_workers[camera_id].row_count = row_count
            stack_writer_workers[camera_id].column_count = column_count
            stack_writer_workers[camera_id].frame_count = tile['frame_count']
            stack_writer_workers[camera_id].x_pos = x_position_mm
            stack_writer_workers[camera_id].y_pos = y_position_mm
            stack_writer_workers[camera_id].z_pos = z_position_mm
            stack_writer_workers[camera_id].x_voxel_size = tile['voxel_size_um']['x']
            stack_writer_workers[camera_id].y_voxel_size = tile['voxel_size_um']['x']
            stack_writer_workers[camera_id].z_voxel_size = tile['voxel_size_um']['x']
            stack_writer_workers[camera_id].path = local_drive
            stack_writer_workers[camera_id].filename = filename
            stack_writer_workers[camera_id].channel = channel
            stack_writer_workers[camera_id].color = tile['hex_color']
            # instrument.cameras[camera_id]['writer']['object'].row_count = row_count
            # instrument.cameras[camera_id]['writer']['object'].column_count = column_count
            # instrument.cameras[camera_id]['writer']['object'].frame_count = tile['frame_count']
            # instrument.cameras[camera_id]['writer']['object'].x_pos = x_position_mm
            # instrument.cameras[camera_id]['writer']['object'].y_pos = y_position_mm
            # instrument.cameras[camera_id]['writer']['object'].z_pos = z_position_mm
            # instrument.cameras[camera_id]['writer']['object'].x_voxel_size = tile['voxel_size_um']['x']
            # instrument.cameras[camera_id]['writer']['object'].y_voxel_size = tile['voxel_size_um']['x']
            # instrument.cameras[camera_id]['writer']['object'].z_voxel_size = tile['voxel_size_um']['x']
            # instrument.cameras[camera_id]['writer']['object'].path = local_drive
            # instrument.cameras[camera_id]['writer']['object'].filename = filename
            # instrument.cameras[camera_id]['writer']['object'].channel = channel
            # instrument.cameras[camera_id]['writer']['object'].color = tile['hex_color']

            chunk_size = stack_writer_workers[camera_id].chunk_count
            chunk_lock[camera_id] = threading.Lock()
            img_buffer[camera_id] = SharedDoubleBuffer((chunk_size, row_count, column_count),
                                            dtype=stack_writer_workers[camera_id].data_type)

            # set up writer and camera
            stack_writer_workers[camera_id].prepare()
            instrument.cameras[camera_id]['object'].prepare()
            stack_writer_workers[camera_id].start()
            instrument.cameras[camera_id]['object'].start(tile['frame_count'])

        frame_index = 0
        chunk_count = math.ceil(tile['frame_count'] / chunk_size)
        remainder = tile['frame_count'] % chunk_size
        last_chunk_size = chunk_size if not remainder else remainder
        last_frame_index = tile['frame_count'] - 1

        # Images arrive serialized in repeating channel order.
        for stack_index in range(tile['frame_count']):
            chunk_index = stack_index % chunk_size
            # Start a batch of pulses to generate more frames and movements.
            if chunk_index == 0:
                chunks_filled = math.floor(stack_index / chunk_size)
                remaining_chunks = chunk_count - chunks_filled
            # Grab camera frame
            for camera_id in instrument.cameras:
                current_frame = instrument.cameras[camera_id]['object'].grab_frame()
                instrument.cameras[camera_id]['object'].get_camera_acquisition_state()
                img_buffer[camera_id].write_buf[chunk_index] = current_frame

            frame_index += 1
            # Dispatch either a full chunk of frames or the last chunk,
            # which may not be a multiple of the chunk size.
            if chunk_index == chunk_size - 1 or stack_index == last_frame_index:
                while not all([w.done_reading.is_set()
                    for _, w in stack_writer_workers.items()]):
               #  while not instrument.cameras[camera_id]['writer']['object'].done_reading.is_set():
                    time.sleep(0.001)
                # Dispatch chunk to each StackWriter compression process.
                # Toggle double buffer to continue writing images.
                # To read the new data, the StackWriter needs the name of
                # the current read memory location and a trigger to start.
                # Lock out the buffer before toggling it such that we
                # don't provide an image from a place that hasn't been
                # written yet.
                for camera_id in instrument.cameras:
                    with chunk_lock[camera_id]:
                        img_buffer[camera_id].toggle_buffers()
                        if stack_writer_workers[camera_id].path is not None:
                            stack_writer_workers[camera_id].shm_name = \
                                img_buffer[camera_id].read_buf_mem_name
                            stack_writer_workers[camera_id].done_reading.clear()

        for camera_id in instrument.cameras:
            stack_writer_workers[camera_id].wait_to_finish()
            instrument.cameras[camera_id]['object'].stop()