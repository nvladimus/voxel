import numpy
import time
import math
import threading
import logging
import shutil
from pathlib import Path
from psutil import virtual_memory
from spim_core.config_base import Config
from voxel.instrument import Instrument
from voxel.writers.data_structures.shared_double_buffer import SharedDoubleBuffer


class AcquisitionBase:

    def __init__(self, instrument: Instrument, config_filename: str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # current working directory
        this_dir = Path(__file__).parent.resolve()
        self.config_path = this_dir / Path(config_filename)
        self.config = Config(str(self.config_path))
        self.instrument = instrument

        @check_disk_space
        @check_system_memory
        def run(self):

            acquisition = self.config.cfg['acquisition']
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
                self.instrument.tiling_stages['ASI MS-8000 x axis']['object'].move_absolute(x_position_mm)
                self.instrument.tiling_stages['ASI MS-8000 y axis']['object'].move_absolute(y_position_mm)
                self.instrument.tiling_stages['ASI MS-8000 z axis']['object'].move_absolute(z_position_mm)

                # filter wheel
                filter_name = tile['filter']
                self.instrument.filter_wheels['ASI FW-1000']['object'].set_filter(filter_name)

                # laser
                laser_power = tile['power_mw']

                # writer
                stack_writer_workers = dict()
                chunk_lock = dict()
                img_buffer = dict()

                for camera_id in self.instrument.cameras:
                    filename = f'{filename_prefix}_x_{tile_num_x:04}_y_{tile_num_y:04}_z_{tile_num_z:04}_ch_{channel}_cam_{camera_id}.ims'
                    row_count = self.instrument.cameras[camera_id]['object'].roi['height_px']
                    column_count = self.instrument.cameras[camera_id]['object'].roi['width_px']
                    stack_writer_workers[camera_id] = self.instrument.cameras[camera_id]['writer']['object']
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

                    chunk_size = stack_writer_workers[camera_id].chunk_count
                    chunk_lock[camera_id] = threading.Lock()
                    img_buffer[camera_id] = SharedDoubleBuffer((chunk_size, row_count, column_count),
                                                    dtype=stack_writer_workers[camera_id].data_type)

                    # set up writer and camera
                    stack_writer_workers[camera_id].prepare()
                    instrument.cameras[camera_id]['object'].prepare()
                    stack_writer_workers[camera_id].start()
                    self.instrument.cameras[camera_id]['object'].start(tile['frame_count'])

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
                        current_frame = self.instrument.cameras[camera_id]['object'].grab_frame()
                        self.instrument.cameras[camera_id]['object'].get_camera_acquisition_state()
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
                    self.instrument.cameras[camera_id]['object'].stop()

        def check_disk_space(self):
            """Checks ext disk space before scan to see if disk has enough space scan
            """
            local_drive = self.config.cfg['acquisition']['storage']['local_drive']
            external_drive = self.config.cfg['acquisition']['storage']['external_drive']

            data_size_gb = 0
            for camera in self.instrument.cameras:
                for tile in self.config.cfg['acquisition']['tiles']:
                    row_count = camera['object'].roi['height_px']
                    column_count = camera['object'].roi['width_px']
                    data_type = camera['writer']['object']['data_type']
                    frame_count = tile['frame_count']
                    data_size_gb += row_count*column_count*frames*numpy.dtype(data_type).itemsize/1e9

            self.log.info(f'dataset size = {data_size_gb} [GB]')

            if est_scan_filesize >= shutil.disk_usage(external_drive).free:
                self.log.error(f"not enough space in local directory: {local_drive}")
                raise

            if est_scan_filesize >= shutil.disk_usage(local_drive).free:
                self.log.error(f"not enough space in external directory: {external_drive}")
                raise

        def check_read_write_speeds(self, size='16Gb', bs='1M', direct=1, numjobs=1, ioengine= 'windowsaio',
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

            local_drive = self.config.cfg['acquisition']['storage']['local_drive']
            external_drive = self.config.cfg['acquisition']['storage']['external_drive']

            for drive in [local_drive, external_drive]:
                test_filename = fr"{drive}\test.txt"
                f = open(test_filename, 'a')  # Create empty file to check reading/writing speed
                f.close()
                try:
                    speed_MB_s = {}
                    for check in ['read', 'write']:
                        output = subprocess.check_output(
                            fr'fio --name=test --filename={test_filename} --size={size} --rw={check} --bs={bs} '
                            fr'--direct={direct} --numjobs={numjobs} --ioengine={ioengine} --iodepth={iodepth} '
                            fr'--runtime={runtime} --startdelay=0 --thread --group_reporting', shell=True)
                        out = str(output)
                        # Converting MiB to MB = (10**6/2**20)
                        speed_MB_s[check] = round(
                            float(out[out.find('BW=') + len('BW='):out.find('MiB/s')]) / (10 ** 6 / 2 ** 20))

                    # converting B/s to MB/s
                    acq_speed_MB_s = (self.cfg.bytes_per_image * (1 / 1000000)) * (1 / self.cfg.get_period_time())

                    if speed_MB_s['write'] <= acq_speed_MB_s:
                        write_too_slow = True
                        self.log.warning(f'{drive} write speed too slow')
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
            for camera in self.instrument.cameras:
                row_count = camera['object'].roi['height_px']
                column_count = camera['object'].roi['width_px']
                data_type = camera['writer']['object']['data_type']
                chunk_size = camera['writer']['object'].CHUNK_SIZE
                # factor of 2 for concurrent chunks being written/read
                memory_gb += 2*row_count*column_count*chunk_size*numpy.dtype(data_type).itemsize/1e9

            free_memory_gb = virtual_memory()[1] / 1e9
            if free_memory_gb < memory_gb:
                raise MemoryError("system does not have enough memory to run."
                                  f"{memory_gb:.1f}[GB] are required but "
                                  f"{free_memory_gb:.1f}[GB] are available.")