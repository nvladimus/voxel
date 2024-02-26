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
from pathlib import Path
from psutil import virtual_memory
from threading import Event, Thread
from ruamel.yaml import YAML
from voxel.instrument import Instrument
from voxel.writers.data_structures.shared_double_buffer import SharedDoubleBuffer

# added data footprint of resolution pyramid
# 1+1/2^3+1/4^3++1/8^3++1/16^3...
IMAGE_PYRAMID_SIZE_RATIO = 1.14285707474

class Acquisition:

    def __init__(self, instrument: Instrument, config_filename: str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # current working directory
        this_dir = Path(__file__).parent.resolve()
        self.deallocating = Event()
        self.config_path = this_dir / Path(config_filename)
        self.config = YAML().load(Path(self.config_path))
        self.acquisition = self.config['acquisition']
        self.instrument = instrument
        self.writers = dict()
        self.transfers = dict()
        self.pre_processes = dict()
        self.intra_processes = dict()
        self.post_processes = dict()
        for operation_type, operation_dict in self.config['acquisition']['operations'].items():
            self._construct_operations(operation_type, operation_dict)
        self._verify_directories()
        self._verify_acquisition()

    def _load_device(self, driver: str, module: str, kwds: dict = dict()):
        """Load in device based on config. Expecting driver, module, and kwds input"""
        self.log.info(f'loading {driver}.{module}')
        __import__(driver)
        device_class = getattr(sys.modules[driver], module)
        return device_class(**kwds)

    def _setup_device(self, device: object, settings: dict):
        """Setup device based on settings dictionary
        :param device: device to be setup
        :param settings: dictionary of attributes, values to set according to config"""
        self.log.info(f'setting up {device}')
        # successively iterate through settings keys
        for key, value in settings.items():
            setattr(device, key, value)

    def _verify_directories(self):
        # check if local directories exist
        for writer_id, writer in self.writers.items():
            local_directory = writer.path
            if not os.path.isdir(local_directory):
                os.mkdir(local_directory)
        # check if external directories exist
        if self.transfers:
            for transfer_id, transfer in self.transfers.items():
                external_directory = transfer.external_directory
                if not os.path.isdir(external_directory):
                    os.mkdir(external_directory)

    def _verify_acquisition(self):
        # check that writers correspond to camera devices
        for camera_id, camera in self.instrument.cameras.items():
            # check that there is an associated writer.
            if camera_id not in self.writers.keys():
                raise ValueError(f'no writer found for camera {camera_id}. check yaml files.')
            # if transfers
            if self.transfers:
                if camera_id not in self.transfers.keys():
                    raise ValueError(f'no transfer found for camera {camera_id}. check yaml files.')
                # if transfers do exist. check that transfers and writers
                # are not the same directory. this would not make sense.
                local_directory = self.writers[camera_id].path
                external_directory = self.transfers[camera_id].external_directory
                if local_directory == external_directory:
                    raise ValueError(f'local and external directory are the same for camera {camera_id}.')               

    def _construct_operations(self, operation_type, operation_dict):
        """Load and setup operations of an acquisition
        :param operation_type: type of operation like writer. Type is specified by yaml
        :param operation_dict: list of dictionaries describing all alike operations of an acquisition
        like {writer0:{}, writer1:{}}"""

        for name, operation in operation_dict.items():
            # name = operation.get('camera_name', 'name') # Get either camera_name or name
            self.log.info(f'constructing {name}')
            driver = operation['driver']
            module = operation['module']
            init = operation.get('init', {})
            operation_object = self._load_device(driver, module, init)
            settings = operation.get('settings', {})
            self._setup_device(operation_object, settings)
            operation_dict = getattr(self, operation_type)
            operation_dict[name] = operation_object

    def _frame_size_mb(self, camera_id: str):
        row_count_px = self.instrument.cameras[camera_id].roi['height_px']
        column_count_px = self.instrument.cameras[camera_id].roi['width_px']
        data_type = self.writers[camera_id].data_type
        frame_size_mb = row_count_px*column_count_px*numpy.dtype(data_type).itemsize/1e6
        return frame_size_mb

    @property
    def _acquisition_rate_hz(self):
        # use master device to determine theoretical instrument speed.
        master_device_name = self.instrument.master_device['name']
        master_device_type = self.instrument.master_device['type']
        # if camera, calculate acquisition rate based on frame time
        if master_device_type == 'cameras':
            acquisition_rate_hz = 1.0 / (self.instrument.cameras[master_device_name].frame_time_ms / 1000)
        # if scanning stage, calculate acquisition rate based on speed and voxel size
        elif master_device_type == 'scanning stages':
            speed_mm_s = self.instrument.scanning_stages[master_device_name].speed_mm_s
            voxel_size_um = tile['voxel_size_um']
            acquisition_rate_hz = speed_mm_s / (voxel_size_um / 1000)
        # if daq, calculate based on task interval time
        elif master_device_type == 'daqs':
            master_task = self.instrument.master_device['task']
            acquisition_rate_hz = 1.0 / self.instrument.daqs[master_device_name].task_time_s[master_task]
        # otherwise assertion, these are the only three supported master devices
        else:
            raise ValueError(f'master device type {master_device_type} is not supported.')
        return acquisition_rate_hz

    def _check_compression_ratio(self, camera_id: str):

        # get the correct camera and writer
        camera = self.instrument.cameras[camera_id]
        writer = self.writers[camera_id]
        if writer.compression == 'none':
            # store initial trigger mode
            initial_trigger = camera.trigger
            # turn trigger off
            # TODO FIX THIS BY JUST REPLACING VALUE
            new_trigger = initial_trigger
            new_trigger['mode'] = 'off'
            camera.trigger = new_trigger

            # prepare the writer
            writer.row_count_px = camera.roi['height_px']
            writer.column_count_px = camera.roi['width_px']
            writer.frame_count_px = writer.chunk_count_px
            writer.filename = 'compression_ratio_test'

            chunk_size = writer.chunk_count_px
            chunk_lock = threading.Lock()
            img_buffer = SharedDoubleBuffer((chunk_size, camera.roi['height_px'], camera.roi['width_px']),
                                            dtype=writer.data_type)

            # set up and start writer and camera
            writer.prepare()
            camera.prepare()
            writer.start()
            camera.start()

            frame_index = 0
            for frame_index in range(writer.frame_count_px):
                # grab camera frame
                current_frame = camera.grab_frame()
                # put into image buffer
                img_buffer.add_image(current_frame)
                frame_index += 1

            while not writer.done_reading.is_set():
                time.sleep(0.001)

            with chunk_lock:
                img_buffer.toggle_buffers()
                if writer.path is not None:
                    writer.shm_name = \
                        img_buffer.read_buf_mem_name
                    writer.done_reading.clear()            

            # close writer and camera
            writer.wait_to_finish()
            camera.stop()

            # reset the trigger
            camera.trigger = initial_trigger

            # clean up the image buffer
            self.deallocating.set()
            self.log.debug(f"deallocating shared double buffer.")
            img_buffer.close_and_unlink()
            del img_buffer
            self.deallocating.clear()

            # check the compressed file size
            filepath = str((writer.path/Path(f"{writer.filename}")).absolute())
            compressed_file_size_mb = os.stat(filepath).st_size / (1024**2)
            # calculate the raw file size
            frame_size_mb = self._frame_size_mb(camera_id)
            raw_file_size_mb = frame_size_mb * writer.frame_count_px
            frame_size_mb = self._frame_size_mb(camera_id)
            # calculate the compression ratio
            compression_ratio = raw_file_size_mb / compressed_file_size_mb

            # delete the files
            writer.delete_files()

        else:
            compression_ratio = 1.0

        return compression_ratio

    def engine(self, tile, filename, camera, writer):

        writer.row_count_px = camera.roi['height_px']
        writer.column_count_px = camera.roi['width_px']
        writer.frame_count_px = tile['frame_count_px']
        writer.x_position_mm = tile['position_mm']['x']
        writer.y_position_mm = tile['position_mm']['y']
        writer.z_position_mm = tile['position_mm']['z']
        writer.x_voxel_size_um = tile['voxel_size_um']['x']
        writer.y_voxel_size_um = tile['voxel_size_um']['x']
        writer.z_voxel_size_um = tile['voxel_size_um']['x']
        writer.theta_deg = tile['theta_deg']
        writer.filename = filename
        writer.channel = tile['channel']

        chunk_size = writer.chunk_count_px
        chunk_lock = threading.Lock()
        img_buffer = SharedDoubleBuffer((chunk_size, camera.roi['height_px'], camera.roi['width_px']),
                                        dtype=writer.data_type)

        # set up and start writer and camera
        writer.prepare()
        camera.prepare()
        writer.start()
        camera.start()

        frame_index = 0
        chunk_count = math.ceil(tile['frame_count_px'] / chunk_size)

        remainder = tile['frame_count_px'] % chunk_size
        last_chunk_size = chunk_size if not remainder else remainder
        last_frame_index = tile['frame_count_px'] - 1

        # Images arrive serialized in repeating channel order.
        for frame_index in range(tile['frame_count_px']):
            chunk_index = frame_index % chunk_size
            # Start a batch of pulses to generate more frames and movements.
            if chunk_index == 0:
                chunks_filled = math.floor(frame_index / chunk_size)
                remaining_chunks = chunk_count - chunks_filled
            # Grab camera frame
            current_frame = camera.grab_frame()
            camera.signal_acquisition_state()
            img_buffer.add_image(current_frame)

            frame_index += 1

            # Dispatch either a full chunk of frames or the last chunk,
            # which may not be a multiple of the chunk size.
            if chunk_index == chunk_size - 1 or frame_index == last_frame_index:
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

        # close writer and camera
        writer.wait_to_finish()
        camera.stop()

        # clean up the image buffer
        self.deallocating.set()
        self.log.debug(f"deallocating shared double buffer.")
        img_buffer.close_and_unlink()
        del img_buffer
        self.deallocating.clear()

    def run(self):

        acquisition_threads = dict()
        transfer_threads = dict()
        filenames = dict()

        # loop over all tiles in acquisition
        for tile in self.config['acquisition']['tiles']:

            # sanity checks
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
                tiling_stage.move_absolute(tile_position)
                # self.log.info(f'moving stage {name} to {instrument_axis} = {tile_position} mm')

            # wait on all stages... simultaneously
            for tiling_stage_id, tiling_stage in self.instrument.tiling_stages.items():
                while tiling_stage.is_axis_moving():
                    time.sleep(0.01)

            # move filter wheels to correct postions
            for filter_wheel_id, filter_wheel in self.instrument.filter_wheels.items():
                filter_wheel_id = filter_wheel.id
                filter_name = tile['filter_index'][filter_wheel_id]
                filter_wheel.filter = filter_name
                # self.log.info(f'moving filter wheel {name} to {filter_wheel_id} = {filter_name}')

            # adjust lasers to correct powers
            # for name, laser in self.instrument.lasers.items():
                # TODO. need to have a way to identify lasers
                # laser_id = laser.wavelength
                # laser_power = tile['power_mm']
                # same approach to adjust as above

            for camera_id, camera in self.instrument.cameras.items():
 
                # filename
                tile_num_x = tile['tile_number']['x']
                tile_num_y = tile['tile_number']['y']
                tile_num_z = tile['tile_number']['z']
                channel = tile['channel']
                prefix = tile["filename_prefix"]
                filename = f'{prefix}_x_{tile_num_x:04}_y_{tile_num_y:04}_z_{tile_num_z:04}_ch_{channel}_cam_{name}'

                # create acquisition threads
                acquisition_threads[camera_id] = threading.Thread(target=self.engine,
                                                             args=(tile,
                                                             filename,
                                                             camera,
                                                             self.writers[camera_id]))
            # start threads
            for name in acquisition_threads:
                acquisition_threads[camera_id].start()

            # join threads and wait
            for name in acquisition_threads:
                acquisition_threads[camera_id].join()

            # handle starting and waiting for file transfers
            if self.transfers:
                for transfer_id in list(transfer_threads.keys()):
                    transfer_thread = transfer_threads.pop(transfer_id)
                    if transfer_thread.is_alive():
                        self.log.info(f"waiting on file transfer for {transfer_id}")
                        transfer_thread.wait_until_finished()
                for writer_id, writer in self.writers.items():
                    transfer_threads[writer_id] = self.transfers[writer_id]
                    transfer_threads[writer_id].local_directory = Path(writer.path)
                    transfer_threads[writer_id].filename = writer.filename
                    self.log.info(f"starting file transfer of {writer.filename} for {writer_id}")
                    transfer_threads[writer_id].start()

        # wait for last tiles file transfer
        if self.transfers:
            for thread_id in list(transfer_threads.keys()):
                transfer_thread = transfer_threads.pop(thread_id)
                if transfer_thread.is_alive():
                    self.log.info(f"waiting on file transfer of for {thread_id}")
                    transfer_thread.wait_until_finished()

        # close hardware
        # TODO. do we need to safely close COM port devices?
        for camera_id, camera in self.instrument.cameras.items():
            camera.close()
        for daq_id, daq in self.instrument.daqs.items():
            daq.close_all()

    def check_local_acquisition_disk_space(self):
        """Checks local and ext disk space before scan to see if disk has enough space scan
        """
        drives = dict()
        for camera_id, camera in self.instrument.cameras.items():
            data_size_gb = 0
            # if windows
            if platform.system() == 'Windows':
                local_drive = os.path.splitdrive(self.writers[camera_id].path)[0]
            # if unix
            else:
                abs_path = os.path.abspath(self.writers[camera_id].path)
                local_drive = '/'
            for tile in self.config['acquisition']['tiles']:
                frame_size_mb = self._frame_size_mb(camera_id)
                frame_count_px = tile['frame_count_px']
                data_size_gb += frame_count_px*frame_size_mb / 1024
            drives.setdefault(local_drive, []).append(data_size_gb)

        for drive in drives:
            required_size_gb = sum(drives[drive])
            self.log.info(f'required disk space = {required_size_gb:.1f} [GB] on drive {drive}')
            free_size_gb = shutil.disk_usage(drive).free / 1024**3
            if data_size_gb >= free_size_gb:
                self.log.error(f"only {free_size_gb:.1f} available on drive: {drive}")
                raise ValueError(f"only {free_size_gb:.1f} available on drive: {drive}")
            else:
                self.log.info(f'available disk space = {free_size_gb:.1f} [GB] on drive {drive}')

    def check_external_acquisition_disk_space(self):
        """Checks local and ext disk space before scan to see if disk has enough space scan
        """
        if self.transfers:
            drives = dict()
            for camera_id, camera in self.instrument.cameras.items():
                data_size_gb = 0
                # if windows
                if platform.system() == 'Windows':
                    external_drive = os.path.splitdrive(self.transfers[camera_id].external_directory)[0]
                # if unix
                else:
                    abs_path = os.path.abspath(self.transfers[camera_id].external_directory)
                    # TODO FIX THIS
                    external_drive = '/'
                for tile in self.config['acquisition']['tiles']:
                    frame_size_mb = self._frame_size_mb(camera_id)
                    frame_count_px = tile['frame_count_px']
                    data_size_gb += frame_count_px*frame_size_mb / 1024
                drives.setdefault(external_drive, []).append(data_size_gb)
            for drive in drives:
                required_size_gb = sum(drives[drive])
                self.log.info(f'required disk space = {required_size_gb:.1f} [GB] on drive {drive}')
                free_size_gb = shutil.disk_usage(drive).free/ 1024**3
                if data_size_gb >= free_size_gb:
                    self.log.error(f"only {free_size_gb:.1f} available on drive: {drive}")
                    raise ValueError(f"only {free_size_gb:.1f} available on drive: {drive}")
                else:
                    self.log.info(f'available disk space = {free_size_gb:.1f} [GB] on drive {drive}')
        else:
            raise ValueError(f'no transfers configured. check yaml files.')

    def check_local_tile_disk_space(self, tile: dict):
        """Checks local and ext disk space before scan to see if disk has enough space scan
        """
        drives = dict()
        for camera_id, camera in self.instrument.cameras.items():
            data_size_gb = 0
            # if windows
            if platform.system() == 'Windows':
                local_drive = os.path.splitdrive(self.writers[camera_id].path)[0]
            # if unix
            else:
                abs_path = os.path.abspath(self.writers[camera_id].path)
                local_drive = '/'

            frame_size_mb = self._frame_size_mb(camera_id)
            frame_count_px = tile['frame_count_px']
            data_size_gb += frame_count_px*frame_size_mb / 1024

            drives.setdefault(local_drive, []).append(data_size_gb)

        for drive in drives:
            required_size_gb = sum(drives[drive])
            self.log.info(f'required disk space = {required_size_gb:.1f} [GB] on drive {drive}')
            free_size_gb = shutil.disk_usage(drive).free/ 1024**3
            if data_size_gb >= free_size_gb:
                self.log.error(f"only {free_size_gb:.1f} available on drive: {drive}")
                raise ValueError(f"only {free_size_gb:.1f} available on drive: {drive}")
            else:
                self.log.info(f'available disk space = {free_size_gb:.1f} [GB] on drive {drive}')

    def check_external_tile_disk_space(self, tile: dict):
        """Checks local and ext disk space before scan to see if disk has enough space scan
        """
        if self.transfers:
            drives = dict()
            for camera_id, camera in self.instrument.cameras.items():
                data_size_gb = 0
                # if windows
                if platform.system() == 'Windows':
                    external_drive = os.path.splitdrive(self.transfers[camera_id].external_directory)[0]
                # if unix
                else:
                    abs_path = os.path.abspath(self.transfers[camera_id].external_directory)
                    # TODO FIX THIS
                    external_drive = '/'
                frame_size_mb = self._frame_size_mb(camera_id)
                frame_count_px = tile['frame_count_px']
                data_size_gb += frame_count_px*frame_size_mb / 1024
                drives.setdefault(external_drive, []).append(data_size_gb)
            for drive in drives:
                required_size_gb = sum(drives[drive])
                self.log.info(f'required disk space = {required_size_gb:.1f} [GB] on drive {drive}')
                free_size_gb = shutil.disk_usage(drive).free/ 1024**3
                if data_size_gb >= free_size_gb:
                    self.log.error(f"only {free_size_gb:.1f} available on drive: {drive}")
                    raise ValueError(f"only {free_size_gb:.1f} available on drive: {drive}")
                else:
                    self.log.info(f'available disk space = {free_size_gb:.1f} [GB] on drive {drive}')
        else:
            raise ValueError(f'no transfers configured. check yaml files.')

    def check_write_speed(self, size='16Gb', bs='1M', direct=1, numjobs=1,
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
        # windows ioengine
        if platform.system() == 'Windows':
            ioengine = 'windowsaio'
        # unix ioengine
        else:
            ioengine = 'posixaio'

        drives = dict()
        camera_speed_mb_s = dict()

        # loop over cameras and see where they are acquiring data
        for camera_id, camera in self.instrument.cameras.items():
            # check the compression ratio for this camera
            compression_ratio = self._check_compression_ratio(camera_id)
            # grab the frame size and acquisition rate
            frame_size_mb = self._frame_size_mb(camera_id)
            acquisition_rate_hz = self._acquisition_rate_hz
            local_directory = self.writers[camera_id].path
            # strip drive letters from paths so that we can combine
            # cameras acquiring to the same drives
            if platform.system() == 'Windows':
                local_drive_letter = os.path.splitdrive(local_directory)[0]
            # if unix
            else:
                # TODO FIX THIS -> what is syntax for unix drives?
                local_abs_path = os.path.abspath(local_directory)
                local_drive_letter = '/'
            # add into drives dictionary append to list if same drive letter
            drives.setdefault(local_drive_letter, []).append(local_directory)
            camera_speed_mb_s.setdefault(local_drive_letter, []).append(acquisition_rate_hz * frame_size_mb / compression_ratio)
            if self.transfers:
                external_directory = self.transfers[camera_id].path
                # strip drive letters from paths so that we can combine
                # cameras acquiring to the same drives
                if platform.system() == 'Windows':
                    external_drive_letter = os.path.splitdrive(local_directory)[0]
                # if unix
                else:
                    # TODO FIX THIS -> what is syntax for unix drives?
                    external_abs_path = os.path.abspath(local_directory)
                    external_drive_letter = '/'
                # add into drives dictionary append to list if same drive letter
                drives.setdefault(external_drive_letter, []).append(external_directory)
                camera_speed_mb_s.setdefault(external_drive_letter, []).append(acquisition_rate_hz * frame_size_mb)              

        for drive in drives:
            # if more than one stream on this drive, just test the first directory location
            local_directory = drives[drive][0]
            test_filename = Path(f'{local_directory}/iotest')
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

                total_speed_mb_s = sum(camera_speed_mb_s[drive])
                # check if drive write speed exceeds the sum of all cameras streaming to this drive
                if write_speed_mb_s < total_speed_mb_s:
                    self.log.warning(f'write speed too slow on drive {drive}')
                    raise ValueError(f'write speed too slow on drive {drive}')

                self.log.info(f'available write speed = {write_speed_mb_s:.1f} [MB/sec] to directory {drive}')
                self.log.info(f'required write speed = {total_speed_mb_s:.1f} [MB/sec] to directory {drive}')

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
        for camera_id, camera in self.instrument.cameras.items():
            row_count_px = camera.roi['height_px']
            column_count_px = camera.roi['width_px']
            # grab the correct writer, name of writer must match name of camera
            try:
                data_type = self.writers[camera_id].data_type
                chunk_count_px = self.writers[camera_id].chunk_count_px
            except:
                raise ValueError(f'no writer found for camera {camera_id}. check yaml files.')
            # factor of 2 for concurrent chunks being written/read
            frame_size_mb = self._frame_size_mb(camera_id)
            memory_gb += 2 * chunk_count_px * frame_size_mb / 1024

        free_memory_gb = virtual_memory()[1] / 1024**3

        self.log.info(f'required RAM = {memory_gb:.1f} [GB]')
        self.log.info(f'available RAM = {free_memory_gb:.1f} [GB]')

        if free_memory_gb < memory_gb:
            raise MemoryError('system does not have enough memory to run')
