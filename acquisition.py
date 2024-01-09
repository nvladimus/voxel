import numpy
import time
import math
import threading
import logging
import sys
import shutil
import os
import subprocess
import ruamel
from pathlib import Path
from psutil import virtual_memory
from spim_core.config_base import Config
from threading import Event, Thread
from instrument import Instrument
from writers.data_structures.shared_double_buffer import SharedDoubleBuffer
from multiprocessing.shared_memory import SharedMemory
from writers.imaris import Writer

MINIMUM_WRITE_SPEED_MB_S = 500

class Acquisition():

    def __init__(self, instrument: Instrument, config_filename: str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # current working directory
        this_dir = Path(__file__).parent.resolve()
        self.config_path = this_dir / Path(config_filename)
        self.config = Config(str(self.config_path))
        self.acquisition = self.config.cfg['acquisition']
        self.instrument = instrument
        self.writers = dict()
        self.storages = dict()
        self.transfers = dict()
        self.transfer_worker_list = dict()
        self.construct_writers(self.acquisition['writers'])
        self.construct_storage(self.acquisition['storage'])
        # self.construct_processes(self.acquisition['processes'])

    def load_device(self, driver: str, module: str, kwds: dict = dict()):
        """Load in device based on config. Expecting driver, module, and kwds input"""
        self.log.info(f'loading {driver}.{module}')
        __import__(driver)
        device_class = getattr(sys.modules[driver], module)
        return device_class(**kwds)

    def setup_device(self, device: object, settings: dict):
        """Setup device based on settings dictionary
        :param device: device to be setup
        :param settings: dictionary of attributes, values to set according to config"""
        self.log.info(f'setting up {device}')
        # successively iterate through settings keys
        for key in settings.keys():
            # determine if key matches an attribute
            if key in dir(device):
                # check if key value is a yaml dictionary
                if type(settings[key]) == ruamel.yaml.comments.CommentedMap:
                    attribute = key
                    # if dictionary, convert to dict and set attribute
                    values = dict(settings[key])
                    setattr(device, attribute, values)
                else:
                    # else set single attribute to single value
                    attribute = key
                    value = settings[key]
                    setattr(device, attribute, value)
            # if no match, check nested settings dictionary
            else:
                nested_settings = settings[key]
                # repeat process of checking nested keys for matches
                for key in nested_settings.keys():
                    if key in dir(device):
                        if type(nested_settings[key]) == ruamel.yaml.comments.CommentedMap:
                            attribute = key
                            values = dict(nested_settings[key])
                            setattr(device, attribute, values)
                        else:
                            attribute = key
                            value = nested_settings[key]
                            setattr(device, attribute, value)
                    else:
                        raise LookupError(f'{key} is not a valid attribute of {type(device)}')

    def engine(self, tile, filename, camera, writer, storage):

        writer.row_count = camera.roi['height_px']
        writer.column_count = camera.roi['width_px']
        writer.frame_count = tile['frame_count']
        writer.x_pos_mm = tile['position_mm']['x']
        writer.y_pos_mm = tile['position_mm']['y']
        writer.z_pos_mm = tile['position_mm']['z']
        writer.x_voxel_size = tile['voxel_size_um']['x']
        writer.y_voxel_size = tile['voxel_size_um']['x']
        writer.z_voxel_size = tile['voxel_size_um']['x']
        writer.path = storage['local_drive']
        writer.filename = filename
        writer.channel = tile['channel']
        writer.color = tile['hex_color']

        chunk_size = writer.chunk_count
        chunk_lock = threading.Lock()
        img_buffer = SharedDoubleBuffer((chunk_size, camera.roi['height_px'], camera.roi['width_px']),
                                        dtype=writer.data_type)

        # set up writer and camera
        writer.prepare()
        camera.prepare()
        writer.start()
        camera.start(tile['frame_count'])

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
            current_frame = camera.grab_frame()
            camera.get_camera_acquisition_state()
            img_buffer.write_buf[chunk_index] = current_frame

            frame_index += 1
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

        writer.wait_to_finish()
        camera.stop()

    def run(self):

        acquisition_threads = dict()
        transfer_threads = dict()
        filenames = dict()

        for tile in self.config.cfg['acquisition']['tiles']:

            # stages
            self.instrument.tiling_stages['ASI MS-8000 x axis'].move_absolute(tile['position_mm']['x'])
            self.instrument.tiling_stages['ASI MS-8000 y axis'].move_absolute(tile['position_mm']['y'])
            self.instrument.tiling_stages['ASI MS-8000 z axis'].move_absolute(tile['position_mm']['z'])

            # filter wheel
            self.instrument.filter_wheels['ASI FW-1000'].set_filter(tile['filter'])

            # laser
            laser_power = tile['power_mw']

            for writer in self.acquisition['writers']:

                # grab camera id
                camera_id = writer['camera_name']

                # filename
                tile_num_x = tile['tile_number']['x']
                tile_num_y = tile['tile_number']['y']
                tile_num_z = tile['tile_number']['z']
                channel = tile['channel']
                filename_prefix = self.storages[camera_id]['filename_prefix']
                filenames[camera_id] = f'{filename_prefix}_x_{tile_num_x:04}_y_{tile_num_y:04}_z_{tile_num_z:04}_ch_{channel}_cam_{camera_id}.ims'

                thread = threading.Thread(target=self.engine,
                    args=(tile, filenames[camera_id],
                            self.instrument.cameras[camera_id],
                            self.writers[camera_id],
                            self.storages[camera_id]))
                acquisition_threads[camera_id] = thread 

            for camera_id in acquisition_threads:
                acquisition_threads[camera_id].start()

            for camera_id in acquisition_threads:
                acquisition_threads[camera_id].join()

            if self.transfers:
                for camera_id in list(transfer_threads.keys()):
                    transfer_thread = transfer_threads.pop(camera_id)
                    if transfer_thread.is_alive():
                        self.log.info(f"waiting on file transfer of {filenames[camera_id]} for {camera_id}")
                        transfer_thread.join()
                for writer in self.acquisition['writers']:
                    camera_id = writer['camera_name']
                    transfer_threads[camera_id] = self.transfers[camera_id]
                    transfer_threads[camera_id].local_drive = Path(self.storages[camera_id]['local_drive'])
                    transfer_threads[camera_id].external_drive = Path(self.storages[camera_id]['external_drive'])
                    transfer_threads[camera_id].filename = filenames[camera_id]

                    self.log.info(f"starting file transfer of {filenames[camera_id]} for {camera_id}")
                    transfer_threads[camera_id].start()

        if self.transfers:
            for camera_id in list(transfer_threads.keys()):
                transfer_thread = transfer_threads.pop(camera_id)
                if transfer_thread.is_alive():
                    self.log.info(f"waiting on file transfer of {filenames[camera_id]} for {camera_id}")
                    transfer_thread.join()

        for daq_id in self.instrument.daqs:
            self.instrument.daqs[daq_id].close_all()

    def construct_storage(self, storage_list: list):
        for storage in storage_list:
            name = storage['camera_name']
            self.storages[name] = storage
            transfer = storage['transfer']
            try:
                init = transfer['init']
                transfer_object = self.load_device(transfer['driver'], transfer['module'], init)
            except:
                transfer_object = self.load_device(transfer['driver'], transfer['module'])
            try:
                settings = transfer['settings']
                self.setup_device(transfer_object, settings)
            except:
                self.log.debug('no settings listed')
            self.transfers[name] = transfer_object

    def construct_writers(self, writers_list: list):

        for writer in writers_list:
            name = writer['camera_name']
            try:
                init = writer['init']
                writer_object = self.load_device(writer['driver'], writer['module'], init)
            except:
                writer_object = self.load_device(writer['driver'], writer['module'])
            try:
                settings = writer['settings']
                self.setup_device(writer_object, settings)
            except:
                self.log.debug('no settings listed')
            self.writers[name] = writer_object

    def construct_processes(self, processes_list: list):

        for process in processes_list['pre']:
            name = process['name']
            try:
                init = process['init']
                process_object = self.load_device(process['driver'], process['module'], init)
            except:
                process_object = self.load_device(process['driver'], process['module'])
            try:
                settings = process['settings']
            except:
                self.log.debug('no settings listed')
            self.setup_device(process_object, settings)
            self.processes[name] = process_object

    def check_disk_space(self):
        """Checks ext disk space before scan to see if disk has enough space scan
        """
        drives = dict()

        for writer in self.acquisition['writers']:
            data_size_gb = 0
            camera_id = writer['camera_name']
            local_drive = os.path.splitdrive(self.storages[camera_id]['local_drive'])[0]
            external_drive = os.path.splitdrive(self.storages[camera_id]['external_drive'])[0]
            for tile in self.config.cfg['acquisition']['tiles']:
                row_count = self.instrument.cameras[camera_id].roi['height_px']
                column_count = self.instrument.cameras[camera_id].roi['width_px']
                data_type = self.writers[camera_id].data_type
                frame_count = tile['frame_count']
                data_size_gb += row_count*column_count*frame_count*numpy.dtype(data_type).itemsize/1e9
            drives.setdefault(local_drive, []).append(data_size_gb)
            drives.setdefault(external_drive, []).append(data_size_gb)

        for drive in drives:
            required_size_gb = sum(drives[drive])
            self.log.info(f'required disk space = {required_size_gb} [GB]')
            free_size_gb = shutil.disk_usage(drive).free/1e9
            if data_size_gb >= free_size_gb:
                self.log.error(f"not enough space in directory: {drive}")
                raise
            else:
                self.log.info(f'available disk space = {free_size_gb} [GB] on drive {drive}\\')

    def check_write_speed(self, size='16Gb', bs='1M', direct=1, numjobs=1, ioengine= 'windowsaio',
                                iodepth=1, runtime=0):
        """Check local read/write speeds to make sure it can keep up with acquisition

        :param size: Size of test file
        :param bs: Block size in bytes used for I/O units
        :param direct: Specifying buffered (0) or unbuffered (1) operation
        :param numjobs: Number of clones of this job. Each clone of job is spawned as an independent thread or process
        :param ioengine: Defines how the job issues I/O to the file
        :param iodepth: Number of I/O units to keep in flight against the file.
        :param runtime: Limit runtime. The test will run until it completes the configured I/O workload or until it has
                        run for this specified amount of time, whichever occurs first
        """

        drives = dict()

        for writer in self.acquisition['writers']:
            camera_id = writer['camera_name']
            local_drive_path = (self.storages[camera_id]['local_drive'])
            external_drive_path = self.storages[camera_id]['external_drive']
            local_drive_letter = os.path.splitdrive(self.storages[camera_id]['local_drive'])[0]
            external_drive_letter = os.path.splitdrive(self.storages[camera_id]['external_drive'])[0]
            drives.setdefault(local_drive_letter, local_drive_path)
            drives.setdefault(external_drive_letter, external_drive_path)

        for drive in drives:
            test_filename = Path(f'{drives[drive]}\\iotest')
            f = open(test_filename, 'a')  # Create empty file to check reading/writing speed
            f.close()
            try:
                output = subprocess.check_output(
                    fr'fio --name=test --filename={test_filename} --size={size} --rw=write --bs={bs} '
                    fr'--direct={direct} --numjobs={numjobs} --ioengine={ioengine} --iodepth={iodepth} '
                    fr'--runtime={runtime} --startdelay=0 --thread --group_reporting', shell=True)
                out = str(output)
                # Converting MiB to MB = (10**6/2**20)
                write_speed_mb_s = round(
                    float(out[out.find('BW=') + len('BW='):out.find('MiB/s')]) / (10 ** 6 / 2 ** 20))

                self.log.info(f'available write speed = {write_speed_mb_s} [MB/sec] to directory {drive}\\')

                if write_speed_mb_s <= MINIMUM_WRITE_SPEED_MB_S:
                    self.log.warning(f'write speed too slow on drive {drive}')
                    raise

            except subprocess.CalledProcessError:
                self.log.warning('fios not installed on computer. Cannot verify read/write speed')
            finally:
                # Delete test file
                os.remove(test_filename)

    def check_system_memory(self):
        """Make sure this machine can image under the specified configuration.

        :param channel_count: the number of channels we want to image with.
        :param mem_chunk: the number of images to hold in one chunk for
            compression
        :raises MemoryError:
        """
        # Calculate double buffer size for all channels.
        memory_gb = 0
        for camera_id in self.instrument.cameras:
            row_count = self.instrument.cameras[camera_id].roi['height_px']
            column_count = self.instrument.cameras[camera_id].roi['width_px']
            data_type = self.writers[camera_id].data_type
            chunk_count = self.writers[camera_id].chunk_count
            # factor of 2 for concurrent chunks being written/read
            memory_gb += 2*row_count*column_count*chunk_count*numpy.dtype(data_type).itemsize/1e9

        free_memory_gb = virtual_memory()[1] / 1e9

        self.log.info(f'required RAM = {memory_gb:.1f} [GB]')
        self.log.info(f'available RAM = {free_memory_gb:.1f} [GB]')

        if free_memory_gb < memory_gb:
            raise MemoryError('system does not have enough memory to run')