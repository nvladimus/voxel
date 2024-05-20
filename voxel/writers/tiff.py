import numpy as np
import logging
import multiprocessing
import re
import os
import sys
import tifffile
from voxel.writers.base import BaseWriter
from multiprocessing import Process, Array, Value, Event
from multiprocessing.shared_memory import SharedMemory
from ctypes import c_wchar
from pathlib import Path
from datetime import datetime
from time import sleep, perf_counter
from math import ceil

CHUNK_COUNT_PX = 64

COMPRESSION_TYPES = {
    "none": "none"
}

DATA_TYPES = {
    "uint8",
    "uint16"
}

class Writer(BaseWriter):

    def __init__(self, path: str):
 
        super().__init__()

        # check path for forward slashes
        if '\\' in path or '/' not in path:
            assert ValueError('path string should only contain / not \\')
        self._path = path
        self._color = None
        self._channel = None
        self._filename = None
        self._data_type = 'uint16'
        self._compression = COMPRESSION_TYPES["none"]
        self._row_count_px = None
        self._colum_count_px = None
        self._frame_count_px = None
        self._z_position_mm = None
        self._y_position_mm = None
        self._x_position_mm = None
        self._z_voxel_size_um = None
        self._y_voxel_size_um = None
        self._x_voxel_size_um = None

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # Opinioated decision on chunking dimension order
        self.chunk_dim_order = ('z', 'y', 'x')
        # Flow control attributes to synchronize inter-process communication.
        self.done_reading = Event()
        self.done_reading.set()  # Set after processing all data in shared mem.
        self.deallocating = Event()

    @property
    def signal_progress_percent(self):
        # convert to %
        state = {'Progress [%]': self.progress.value*100}
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
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, data_type: np.unsignedinteger):
        self.log.info(f'setting data type to: {data_type}')
        self._data_type = data_type

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path: str or path):
        if '\\' in str(path) or '/' not in str(path):
            self.log.error('path string should only contain / not \\')
        else:
            self._path = str(path)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self._filename = filename \
            if filename.endswith(".tiff") else f"{filename}.tiff"
        self.log.info(f'setting filename to: {filename}')

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, channel: str):
        self.log.info(f'setting channel name to: {channel}')
        self._channel = channel

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
        self.progress = multiprocessing.Value('d', 0.0)
        self.p = Process(target=self._run, args=(self.progress,))
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

    def start(self):
        self.log.info(f"{self._filename}: starting writer.")
        self.p.start()

    def _run(self, shared_progress):
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
        filepath = str((Path(self._path) / self._filename).absolute())

        writer = tifffile.TiffWriter(filepath,
                                     bigtiff=True)


        metadata = {
            'axes': 'ZYX',
            'PhysicalSizeX': self._x_voxel_size_um_um,
            'PhysicalSizeXUnit': 'um',
            'PhysicalSizeY': self._y_voxel_size_um_um,
            'PhysicalSizeYUnit': 'um',
            'PhysicalSizeZ': self._z_voxel_size_um_um,
            'PhysicalSizeZUnit': 'um',
            'Channel': {'Name': [self._channel]},
            'Plane': {
                        'PositionX': self._x_position_mm,
                        'PositionXUnit': 'um',
                        'PositionY': self._y_position_mm,
                        'PositionYUnit': 'um',
                        'PositionZ': self._z_position_mm,
                        'PositionZUnit': 'um',
            }
        }

        chunk_total = ceil(self._frame_count_px_px/CHUNK_COUNT_PX)
        for chunk_num in range(chunk_total):
            # Wait for new data.
            while self.done_reading.is_set():
                sleep(0.001)
            # Attach a reference to the data from shared memory.
            shm = SharedMemory(self.shm_name, create=False, size=self.shm_nbytes)
            frames = np.ndarray(self.shm_shape, self._data_type, buffer=shm.buf)
            logger.warning(f"{self._filename}: writing chunk "
                  f"{chunk_num+1}/{chunk_total} of size {frames.shape}.")
            start_time = perf_counter()
            writer.write(data=frames, metadata=metadata, compression=self._compression)
            frames = None
            logger.warning(f"{self._filename}: writing chunk took "
                  f"{perf_counter() - start_time:.3f} [s]")
            shm.close()
            self.done_reading.set()
            shared_progress.value = (chunk_num+1)/chunk_total

        # Wait for file writing to finish.
        if shared_progress.value < 1.0:
            logger.warning(f"{self._filename}: waiting for data writing to complete for "
                  f"{self._filename}. "
                  f"current progress is {100*shared_progress.value:.1f}%.")
        while shared_progress.value < 1.0:
            sleep(0.5)
            logger.warning(f"{self._filename}: waiting for data writing to complete for "
                  f"{self._filename}. "
                  f"current progress is {100*shared_progress.value:.1f}%.")

        writer.close()

    def wait_to_finish(self):
        self.log.info(f"{self._filename}: waiting to finish.")
        self.p.join()
        # log the finished writer %
        self.signal_progress_percent

    def delete_files(self):
        filepath = str((self._path / Path(f"{self._filename}")).absolute())
        os.remove(filepath)