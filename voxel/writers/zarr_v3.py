import numpy as np
import logging
import multiprocessing
import re
import os
import sys
import tifffile
import tensorstore as ts
import shutil
from voxel.writers.base import BaseWriter
from multiprocessing import Process, Array, Value, Event
from multiprocessing.shared_memory import SharedMemory
from ctypes import c_wchar
from pathlib import Path
from datetime import datetime
from time import sleep, perf_counter
from math import ceil, log2
from sympy import divisors

CHUNK_COUNT_PX = 32
DIVISIBLE_FRAME_COUNT_PX = 32

CHUNK_SIZE_X = 256
CHUNK_SIZE_Y = 256

COMPRESSION_TYPES = [
    "blosclz",
    "lz4",
    "lz4hc",
    "snappy",
    "zlib",
    "zstd",
    "none"
]

COMPRESSION_LEVELS = range(0,9)

SHUFFLE_TYPES = [
    "shuffle",
    "bitshuffle",
    "noshuffle"
]

DATA_TYPES = [
    "uint8",
    "uint16"
]

# tensorstore currently doesn't natively do multi-scale generation
# we have to do it ourselves, can choose from these implemented methods
DOWNSAMPLE_METHOD = [
    "tensorstore",
    "cpu",
    "gpu_tools",
    "gpu_clesperanto",
    "gpu_cucim"
]

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
        self._data_type = "uint16"
        self._compression = "none"
        self._shuffle = "noshuffle"
        self._downsample_method = "cpu"
        self._rows = None
        self._colum_count = None
        self._frame_count = None
        self._z_pos_mm = None
        self._y_pos_mm = None
        self._x_pos_mm = None
        self._z_voxel_size = None
        self._y_voxel_size = None
        self._x_voxel_size = None

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
        return self._x_voxel_size_um

    @x_voxel_size_um.setter
    def x_voxel_size_um(self, x_voxel_size_um: float):
        self.log.info(f'setting x voxel size to: {x_voxel_size_um} [um]')
        self._x_voxel_size_um = x_voxel_size_um

    @property
    def y_voxel_size_um(self):
        return self._y_voxel_size_um

    @y_voxel_size_um.setter
    def y_voxel_size_um(self, y_voxel_size_um: float):
        self.log.info(f'setting y voxel size to: {y_voxel_size_um} [um]')
        self._y_voxel_size_um = y_voxel_size_um

    @property
    def z_voxel_size_um(self):
        return self._z_voxel_size_um

    @z_voxel_size_um.setter
    def z_voxel_size_um(self, z_voxel_size_um: float):
        self.log.info(f'setting z voxel size to: {z_voxel_size_um} [um]')
        self._z_voxel_size_um = z_voxel_size_um

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
        return self._frame_count_px

    @frame_count_px.setter
    def frame_count_px(self, frame_count_px: int):
        self.log.info(f'setting frame count to: {frame_count_px} [px]')
        frame_count_px = ceil(frame_count_px / DIVISIBLE_FRAME_COUNT_PX) * DIVISIBLE_FRAME_COUNT_PX
        self.log.info(f'adjusting frame count to: {frame_count_px} [px]')
        self._frame_count_px = frame_count_px

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
        return self._compression

    @compression.setter
    def compression(self, compression: str):
        if compression not in COMPRESSION_TYPES:
            raise ValueError("compression type must be one of %r." % COMPRESSION_TYPES)
        self.log.info(f'setting compression mode to: {compression}')
        self._compression = compression

    @property
    def shuffle(self):
        return self._shuffle

    @shuffle.setter
    def shuffle(self, shuffle: str):
        if shuffle not in SHUFFLE_TYPES:
            raise ValueError("shuffle type must be one of %r." % SHUFFLE_TYPES)
        self.log.info(f'setting shuffle type to: {shuffle}')
        self._shuffle = shuffle

    @property
    def compression_level(self):
        return self._compression_level

    @compression_level.setter
    def compression_level(self, compression_level: int):
        if compression_level not in COMPRESSION_LEVELS:
            raise ValueError("compression level must be one of %r." % COMPRESSION_LEVELS)
        self.log.info(f'setting compression level to: {compression_level}')
        self._compression_level = compression_level

    @property
    def downsample_method(self):
        return self._downsample_method

    @downsample_method.setter
    def downsample_method(self, downsample_method: str):
        if downsample_method not in DOWNSAMPLE_METHOD:
            raise ValueError("downsample method type must be one of %r." % DOWNSAMPLE_METHOD)
        self.log.info(f'setting downsample method type to: {downsample_method}')
        self._downsample_method = downsample_method

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, data_type: np.unsignedinteger):
        if data_type not in DATA_TYPES:
            raise ValueError("data type must be one of %r." % DATA_TYPES)
        self.log.info(f'setting data type to: {data_type}')
        self._data_type = data_type

    @property
    def path(self):
        return self._path

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self._filename = filename \
            if filename.endswith(".zarr") else f"{filename}.zarr"
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

        # initialize the downsampler
        if self._downsample_method == "cpu":
            from voxel.processes.cpu.downsample_3d import DownSample3D
        elif self._downsample_method == "gpu_tools":
            from voxel.processes.gpu.gputools.downsample_3d import DownSample3D
        elif self._downsample_method == "gpu_clesperanto":
            from voxel.processes.gpu.clesperanto.downsample_3d import DownSample3D
        elif self._downsample_method == "gpu_cucim":
            from voxel.processes.gpu.cucim.downsample_3d import DownSample3D
        downsample = DownSample3D(binning=2)

        # determine the number of pyramid levels
        PYRAMID_LEVELS = min([int(log2(CHUNK_COUNT_PX)),
                              int(log2(self._row_count_px // CHUNK_SIZE_X)),
                              int(log2(self._column_count_px // CHUNK_SIZE_Y))])

        # round the zarr array size in x, y, z to be an integer multiple of the shard size
        store_size_x = int(ceil(self._column_count_px/CHUNK_SIZE_X)*CHUNK_SIZE_X) 
        store_size_y = int(ceil(self._row_count_px/CHUNK_SIZE_Y)*CHUNK_SIZE_Y)
        store_size_z = int(ceil(self._frame_count_px/CHUNK_COUNT_PX)*CHUNK_COUNT_PX)

        # determine the compatible chunk sizes for each level
        chunk_size_x = list()
        chunk_size_y = list()
        for level in range(PYRAMID_LEVELS):
            # get divisible factors using sympy
            factors_x = divisors(store_size_x // 2**level)
            factors_y = divisors(store_size_y // 2**level)
            # find the value closest to the original CHUNK_SIZE_X
            chunk_size_x.append(min(factors_x, key=lambda x:abs(x - CHUNK_SIZE_X)))
            chunk_size_y.append(min(factors_y, key=lambda y:abs(y - CHUNK_SIZE_Y)))

        # initialize the tensorstores for each pyramid level
        writers = list()
        for level in range(PYRAMID_LEVELS):
            # NEED TO ADD LOGIC HERE TO ADJUST CHUNK_SIZE_X/Y based on the level if it is not a clean number i.e. 2048
            # create the compression codec
            if self._compression != "none":
                codec = {"driver": "zarr3", "codecs": [{"name": "blosc",
                                                "configuration": {"cname": self._compression, "clevel": self._compression_level,
                                                "shuffle": self._shuffle}}]}
                writers.append(ts.open({"driver": "zarr3", "kvstore": f"file://{filepath}/res{level}", "create": True, "delete_existing": True},
                        chunk_layout = ts.ChunkLayout(read_chunk_shape=[CHUNK_COUNT_PX // 2**level, chunk_size_y[level], chunk_size_x[level]],
                                                      write_chunk_shape=[CHUNK_COUNT_PX // 2**level, store_size_y // 2**level, store_size_x // 2**level]),
                        dtype=ts.uint16,
                        shape=[store_size_z // 2**level, store_size_y // 2**level, store_size_x // 2**level],
                        codec=ts.CodecSpec(codec)
                ).result())
            # no compresion, omit codec arg
            else:
                writers.append(ts.open({"driver": "zarr3", "kvstore": f"file://{filepath}", "create": True, "delete_existing": True},
                        chunk_layout = ts.ChunkLayout(read_chunk_shape=[CHUNK_COUNT_PX // 2**level, chunk_size_y[level], chunk_size_x[level]],
                                                      write_chunk_shape=[CHUNK_COUNT_PX // 2**level, store_size_y // 2**level, store_size_x // 2**level]),
                        dtype=ts.uint16,
                        shape=[store_size_z // 2**level, store_size_y // 2**level, store_size_x // 2**level]
                ).result())

        chunk_total = ceil(self._frame_count_px/CHUNK_COUNT_PX)
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
            # recursively write all resolution levels
            # this is a none blocking call
            write_futures = list()
            for level in range(PYRAMID_LEVELS):
                # downsample if level > 0
                if level > 0:
                    frames = downsample.run(frames)
                index_min_x = 0 
                index_max_x = frames.shape[2]
                index_min_y = 0 
                index_max_y = frames.shape[1]
                index_min_z = chunk_num*CHUNK_COUNT_PX // 2**level
                index_max_z = (chunk_num+1)*CHUNK_COUNT_PX // 2**level
                write_futures.append(writers[level][index_min_z:index_max_z, index_min_y:index_max_y, index_min_x:index_max_x].write(frames))
            # this is the equivalent of joining each tensorstore write process
            for level in range(PYRAMID_LEVELS):
                write_futures[level].result()
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

    def wait_to_finish(self):
        self.log.info(f"{self._filename}: waiting to finish.")
        self.p.join()
        # log the finished writer %
        self.signal_progress_percent

    def delete_files(self):
        filepath = str((self._path / Path(f"{self._filename}")).absolute())
        shutil.rmtree(filepath)