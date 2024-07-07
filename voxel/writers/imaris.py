import numpy as np
import logging
import multiprocessing
import re
import os
import sys
from voxel.writers.base import BaseWriter
from multiprocessing import Process, Array, Event
from multiprocessing.shared_memory import SharedMemory
from ctypes import c_wchar
from PyImarisWriter import PyImarisWriter as pw
from pathlib import Path
from datetime import datetime
from matplotlib.colors import hex2color
from time import sleep, perf_counter
from math import ceil

CHUNK_COUNT_PX = 64
DIVISIBLE_FRAME_COUNT_PX = 64

COMPRESSION_TYPES = {
    "lz4shuffle":  pw.eCompressionAlgorithmShuffleLZ4,
    "none": pw.eCompressionAlgorithmNone,
}

DATA_TYPES = [
    "uint8",
    "uint16"
]

class ImarisProgressChecker(pw.CallbackClass):
    """Class for tracking progress of an active ImarisWriter disk-writing
    operation."""

    def __init__(self):
        self.progress = 0  # a float representing the progress (0 to 1.0).

    def RecordProgress(self, progress, total_bytes_written):
        self.progress = progress

class Writer(BaseWriter):

    def __init__(self, path: str):
 
        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._path = Path(path)
        self._color = '#ffffff' # initialize as white
        self._channel = None
        self._filename = None
        self._acquisition_name = Path()
        self._data_type = 'uint16'
        self._compression = COMPRESSION_TYPES["none"]
        self._row_count_px = None
        self._colum_count_px_px = None
        self._frame_count_px_px = None
        self._x_voxel_size_um_um = 1
        self._y_voxel_size_um_um = 1
        self._z_voxel_size_um_um = 1
        self._x_position_mm = 0
        self._y_position_mm = 0
        self._z_position_mm = 0
        self._theta_deg = 0
        self._channel = None
        self.progress = 0
        # Opinioated decision on chunking dimension order
        self.chunk_dim_order = ('z', 'y', 'x')
        # Flow control attributes to synchronize inter-process communication.
        self.done_reading = Event()
        self.done_reading.set()  # Set after processing all data in shared mem.
        self.deallocating = Event()
        # Internal flow control attributes to monitor compression progress.
        self.callback_class = ImarisProgressChecker()

    @property
    def signal_progress_percent(self):
        # convert to %
        state = {'Progress [%]': self.progress*100}
        return state

    @property
    def x_voxel_size_um(self):
        return self._x_voxel_size_um_um

    @x_voxel_size_um.setter
    def x_voxel_size_um(self, x_voxel_size_um: float):
        self.log.info(f'setting x voxel size to: {x_voxel_size_um} [um]')
        self._x_voxel_size_um_um = x_voxel_size_um

    @property
    def y_voxel_size_um(self):
        return self._y_voxel_size_um_um

    @y_voxel_size_um.setter
    def y_voxel_size_um(self, y_voxel_size_um: float):
        self.log.info(f'setting y voxel size to: {y_voxel_size_um} [um]')
        self._y_voxel_size_um_um = y_voxel_size_um

    @property
    def z_voxel_size_um(self):
        return self._z_voxel_size_um_um

    @z_voxel_size_um.setter
    def z_voxel_size_um(self, z_voxel_size_um: float):
        self.log.info(f'setting z voxel size to: {z_voxel_size_um} [um]')
        self._z_voxel_size_um_um = z_voxel_size_um

    @property
    def x_position_mm(self):
        return self._x_position_mm

    @x_position_mm.setter
    def x_position_mm(self, x_position_mm: float):
        self.log.info(f'setting x position to: {x_position_mm} [mm]')
        self._x_position_mm = x_position_mm

    @property
    def y_position_mm(self):
        return self._y_position_mm

    @y_position_mm.setter
    def y_position_mm(self, y_position_mm: float):
        self.log.info(f'setting y position to: {y_position_mm} [mm]')
        self._y_position_mm = y_position_mm

    @property
    def z_position_mm(self):
        return self._z_position_mm

    @z_position_mm.setter
    def z_position_mm(self, z_position_mm: float):
        self.log.info(f'setting z position to: {z_position_mm} [mm]')
        self._z_position_mm = z_position_mm

    @property
    def frame_count_px(self):
        return self._frame_count_px_px

    @frame_count_px.setter
    def frame_count_px(self, frame_count_px: int):
        self.log.info(f'setting frame count to: {frame_count_px} [px]')
        frame_count_px = ceil(frame_count_px / DIVISIBLE_FRAME_COUNT_PX) * DIVISIBLE_FRAME_COUNT_PX
        self.log.info(f'adjusting frame count to: {frame_count_px} [px]')
        self._frame_count_px_px = frame_count_px

    @property
    def column_count_px(self):
        return self._column_count_px

    @column_count_px.setter
    def column_count_px(self, column_count_px: int):
        self.log.info(f'setting column count to: {column_count_px} [px]')
        self._column_count_px = column_count_px

    @property
    def row_count_px(self):
        return self._row_count_px

    @row_count_px.setter
    def row_count_px(self, row_count_px: int):
        self.log.info(f'setting row count to: {row_count_px} [px]')
        self._row_count_px = row_count_px

    @property
    def chunk_count_px(self):
        return CHUNK_COUNT_PX

    @property
    def compression(self):
        return next(key for key, value in COMPRESSION_TYPES.items() if value == self._compression)

    @compression.setter
    def compression(self, compression: str):
        valid = list(COMPRESSION_TYPES.keys())
        if compression not in valid:
            raise ValueError("compression type must be one of %r." % valid)
        self.log.info(f'setting compression mode to: {compression}')
        self._compression = COMPRESSION_TYPES[compression]

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, data_type: np.unsignedinteger):
        self.log.info(f'setting data type to: {data_type}')
        self._data_type = data_type

    @property
    def path(self):
        return self._path

    @property
    def acquisition_name(self):
        return self._acquisition_name

    @acquisition_name.setter
    def acquisition_name(self, acquisition_name: str):
        self._acquisition_name = Path(acquisition_name)
        self.log.info(f'setting acquisition name to: {acquisition_name}')

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self._filename = filename \
            if filename.endswith(".ims") else f"{filename}.ims"
        self.log.info(f'setting filename to: {filename}')

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, channel: str):
        self.log.info(f'setting channel name to: {channel}')
        self._channel = channel

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color: str):
        if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
            self._color = color
        else:
            raise ValueError("%r is not a valid hex color code." % color)
        self.log.info(f'setting color to: {color}')

    @property
    def shm_name(self):
        """Convenience getter to extract the shared memory address (string)
        from the c array."""
        return str(self._shm_name[:]).split('\x00')[0]

    @shm_name.setter
    def shm_name(self, name: str):
        """Convenience setter to set the string value within the c array."""
        for i, c in enumerate(name):
            self._shm_name[i] = c
        self._shm_name[len(name)] = '\x00'  # Null terminate the string.
        self.log.info(f'setting shared memory to: {name}')

    def prepare(self):
        self.p = Process(target=self._run)
        # Specs for reconstructing the shared memory object.
        self._shm_name = Array(c_wchar, 32)  # hidden and exposed via property.
        # This is almost always going to be: (chunk_size, rows, columns).
        chunk_shape_map = {'x': self._column_count_px,
           'y': self._row_count_px,
           'z': CHUNK_COUNT_PX}
        self.shm_shape = [chunk_shape_map[x] for x in self.chunk_dim_order]
        self.shm_nbytes = \
            int(np.prod(self.shm_shape, dtype=np.int64)*np.dtype(self._data_type).itemsize)
        self.log.info(f"{self._filename}: intializing writer.")
        self.application_name = 'PyImarisWriter'
        self.application_version = '1.0.0'
        # voxel size metadata to create the converter
        image_size_z = int(ceil(self._frame_count_px_px/CHUNK_COUNT_PX)*CHUNK_COUNT_PX)
        self.image_size = pw.ImageSize(x=self._column_count_px, y=self._row_count_px, z=image_size_z,
                          c=1, t=1)
        self.block_size = pw.ImageSize(x=self._column_count_px, y=self._row_count_px, z=CHUNK_COUNT_PX,
                                  c=1, t=1)
        self.sample_size = pw.ImageSize(x=1, y=1, z=1, c=1, t=1)
        # compute the start/end extremes of the enclosed rectangular solid.
        # (x0, y0, z0) position (in [um]) of the beginning of the first voxel,
        # (xf, yf, zf) position (in [um]) of the end of the last voxel.
        x0 = self._x_position_mm - (self._x_voxel_size_um_um * 0.5 * self._column_count_px)
        y0 = self._y_position_mm - (self._y_voxel_size_um_um * 0.5 * self._row_count_px)
        z0 = self._z_position_mm
        xf = self._x_position_mm + (self._x_voxel_size_um_um * 0.5 * self._column_count_px)
        yf = self._y_position_mm + (self._y_voxel_size_um_um * 0.5 * self._row_count_px)
        zf = self._z_position_mm + self._frame_count_px_px * self._z_voxel_size_um_um
        self.image_extents = pw.ImageExtents(-x0, -y0, -z0, -xf, -yf, -zf)
        # c = channel, t = time. These fields are unused for now.
        # Note: ImarisWriter performs MUCH faster when the dimension sequence
        #   is arranged: x, y, z, c, t.
        #   It is more efficient to transpose/reshape the data into this
        #   shape beforehand instead of defining an arbitrary
        #   DimensionSequence and passing the chunk data in as-is.
        self.chunk_dim_order = ('z', 'y', 'x')
        self.dimension_sequence = pw.DimensionSequence('x', 'y', 'z', 'c', 't')
        # lookups for deducing order
        self.dim_map = {'x': 0, 'y': 1, 'z': 2, 'c': 3, 't': 4}
        # name parameters
        self.parameters = pw.Parameters()
        self.parameters.set_channel_name(0, self._channel)
        # create options object
        self.opts = pw.Options()
        self.opts.mEnableLogProgress = True
        # set threads to double number of cores
        self.thread_count = 2*multiprocessing.cpu_count()
        self.opts.mNumberOfThreads = self.thread_count
        # set compression type
        self.opts.mCompressionAlgorithmType = self._compression
        # color parameters
        self.adjust_color_range = False
        self.color_infos = [pw.ColorInfo()]
        self.color_infos[0].set_base_color(pw.Color(*(*hex2color(self._color), 1.0)))
        # date time parameters
        self.time_infos = [datetime.today()]

    def start(self):
        self.log.info(f"{self._filename}: starting writer.")
        self.p.start()

    def _run(self):
        """Loop to wait for data from a specified location and write it to disk
        as an Imaris file. Close up the file afterwards.

        This function executes when called with the start() method.
        """
        # internal logger for process
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s'
        datefmt = '%Y-%m-%d,%H:%M:%S'
        log_formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        filepath = Path(self._path, self._acquisition_name, self._filename).absolute()
        converter = \
            pw.ImageConverter(self._data_type, self.image_size, self.sample_size,
                              self.dimension_sequence, self.block_size, filepath, 
                              self.opts, self.application_name,
                              self.application_version, self.callback_class)
        chunk_total = ceil(self._frame_count_px_px/CHUNK_COUNT_PX)
        for chunk_num in range(chunk_total):
            block_index = pw.ImageSize(x=0, y=0, z=chunk_num, c=0, t=0)
            # Wait for new data.
            while self.done_reading.is_set():
                sleep(0.001)
            # Attach a reference to the data from shared memory.
            shm = SharedMemory(self.shm_name, create=False, size=self.shm_nbytes)
            frames = np.ndarray(self.shm_shape, self._data_type, buffer=shm.buf)
            logger.warning(f"{self._filename}: writing chunk "
                  f"{chunk_num+1}/{chunk_total} of size {frames.shape}.")
            start_time = perf_counter()
            dim_order = [self.dim_map[x] for x in self.chunk_dim_order]
            # Put the frames back into x, y, z, c, t order.
            converter.CopyBlock(frames.transpose(dim_order), block_index)
            frames = None
            logger.warning(f"{self._filename}: writing chunk took "
                  f"{perf_counter() - start_time:.3f} [s]")
            shm.close()
            self.done_reading.set()

        # Wait for file writing to finish.
        if self.callback_class.progress < 1.0:
            logger.warning(f"{self._filename}: waiting for data writing to complete for "
                  f"{self._filename}. "
                  f"current progress is {100*self.callback_class.progress:.1f}%.")
        while self.callback_class.progress < 1.0:
            sleep(0.5)
            logger.warning(f"{self._filename}: waiting for data writing to complete for "
                  f"{self._filename}. "
                  f"current progress is {100*self.callback_class.progress:.1f}%.")

        converter.Finish(self.image_extents, self.parameters, self.time_infos,
                              self.color_infos, self.adjust_color_range)
        converter.Destroy()

    def wait_to_finish(self):
        self.log.info(f"{self._filename}: waiting to finish.")
        self.p.join()
        # log the finished writer %
        self.signal_progress_percent

    def delete_files(self):
        filepath = Path(self._path, self._acquisition_name, self._filename).absolute()
        os.remove(filepath)