import numpy as np
import logging
import multiprocessing
import re
import os
import sys
from voxel.writers.base import BaseWriter
from voxel.writers.bdv_writer import npy2bdv
from multiprocessing import Process, Array, Value, Event
from multiprocessing.shared_memory import SharedMemory
from ctypes import c_wchar
from pathlib import Path
from datetime import datetime
from time import sleep, perf_counter
from math import ceil

CHUNK_COUNT_PX = 128
DIVISIBLE_FRAME_COUNT_PX = 128
B3D_QUANT_SIGMA = 1 # quantization step
B3D_COMPRESSION_MODE = 1
B3D_BACKGROUND_OFFSET = 0 # ADU
B3D_GAIN = 2.1845 # ADU/e-
B3D_READ_NOISE = 1.5 # e-

COMPRESSION_TYPES = {
    "none":  None,
    "gzip": "gzip",
    "lzf": "lzf",
    "b3d": "b3d"
}

DATA_TYPES = [
    "uint16"
]

class Writer(BaseWriter):

    def __init__(self, path: str):
 
        super().__init__()
        # check path for forward slashes
        if '\\' in path or '/' not in path:
            assert ValueError('path string should only contain / not \\')
        self._path = path
        self._color = '#ffffff' # initialize as white
        self._channel = None
        self._filename = None
        self._data_type = "uint16"
        self._compression = COMPRESSION_TYPES["none"]
        self.compression_opts = None
        self._row_count_px = None
        self._colum_count_px = None
        self._frame_count_px = None
        self._x_voxel_size_um = 1
        self._y_voxel_size_um = 1
        self._z_voxel_size_um = 1
        self._x_position_mm = 0
        self._y_position_mm = 0
        self._z_position_mm = 0
        self._theta_deg = 0
        self._channel = None
        
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # Opinioated decision on chunking dimension order
        self.chunk_dim_order = ('z', 'y', 'x')
        # Flow control attributes to synchronize inter-process communication.
        self.done_reading = Event()
        self.done_reading.set()  # Set after processing all data in shared mem.
        self.deallocating = Event()

        # Lists for storing all datasets in a single BDV file
        self.current_tile_num = 0
        self.current_channel_num = 0
        self.tile_list = list()
        self.channel_list = list()
        self.dataset_dict = dict()
        self.voxel_size_dict = dict()
        self.affine_deskew_dict = dict()
        self.affine_scale_dict = dict()
        self.affine_shift_dict = dict()

    @property
    def signal_progress_percent(self):
        state = {'Progress [%]': self.progress.value*100}
        self.log.info(f'Progress [%]: {self.progress.value*100}')
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
    def theta_deg(self):
        return self._theta_deg

    @theta_deg.setter
    def theta_deg(self, theta_deg: float):
        self.log.info(f'setting theta to: {theta_deg} [deg]')
        self._theta_deg = theta_deg

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
        return next(key for key, value in COMPRESSION_TYPES.items() if value == self._compression)

    @compression.setter
    def compression(self, compression: str):
        valid = list(COMPRESSION_TYPES.keys())
        if compression not in valid:
            raise ValueError("compression type must be one of %r." % valid)
        self.log.info(f'setting compression mode to: {compression}')
        self._compression = COMPRESSION_TYPES[compression]
        # handle compresion opts for b3d
        if compression == "b3d":
            # check for windows os
            if os.name != "nt":
                raise ValueError("b3d compression is only supported on windows")
            # check for hdf5 version
            try:
                import hdf5
            except:
                raise ValueError("hdf5 is not installed")
            hdf5_ver = hdf5.__version__
            if int(hdf5_ver[hdf5_ver.find('.')+1]) > 8:
                raise ValueError("b3d compression is only supported for hdf5 1.8.xx")
            self.compression_opts=(
                int(B3D_QUANT_SIGMA*1000), 
                B3D_COMPRESSION_MODE, 
                int(B3D_GAIN), 
                int(B3D_BACKGROUND_OFFSET), 
                int(B3D_READ_NOISE*1000),
            )

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
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self._filename = filename \
            if filename.endswith(".h5") else f"{filename}.h5"
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
        
        # Check if tile position already exists
        tile_position = (self._x_position_mm, self._y_position_mm, self._z_position_mm)
        if tile_position not in self.tile_list:
            self.tile_list.append(tile_position)
        self.current_tile_num = self.tile_list.index(tile_position)
        
        # Check if tile channel already exists
        if self._channel not in self.channel_list:
            self.channel_list.append(self._channel)
        self.current_channel_num = self.channel_list.index(self._channel)
        
        # Add dimensions to dictionary with key (tile#, channel#)
        tile_dimensions = (self._frame_count_px, self._row_count_px, self._column_count_px)
        self.dataset_dict[(self.current_tile_num, self.current_channel_num)] = tile_dimensions
        
        # Add voxel size to dictionary with key (tile#, channel#)
        # effective voxel size in x direction
        size_x = self._x_voxel_size_um
        # effective voxel size in y direction
        size_y = self._y_voxel_size_um*np.cos(self._theta_deg*np.pi/180.0)
        # effective voxel size in z direction (scan)
        size_z = self._z_voxel_size_um
        voxel_sizes = (size_z, size_y, size_x)
        self.voxel_size_dict[(self.current_tile_num, self.current_channel_num)] = voxel_sizes
        
        # Create affine matrix dictionary with key (tile#, channel#)
        # normalized scaling in x
        scale_x = size_x/size_y
        # normalized scaling in y
        scale_y = size_y/size_y
        # normalized scaling in z (scan)
        scale_z = size_z/size_y
        # shearing based on theta and y/z pixel sizes
        shear = -np.tan(self._theta_deg*np.pi/180.0)*size_y/size_z
        # shift tile in x, unit pixels
        shift_x = scale_x*(self._x_position_mm*1000/size_x)
        # shift tile in y, unit pixels
        shift_y = scale_y*(self._y_position_mm*1000/size_y)
        # shift tile in y, unit pixels
        shift_z = scale_z*(self._z_position_mm*1000/size_z)

        affine_deskew = np.array(
                            ([1.0, 0.0, 0.0, 0.0],
                             [0.0, 1.0, 0.0, 0.0],
                             [0.0, shear, 1.0, 0.0]))

        affine_scale = np.array(
                            ([scale_x, 0.0, 0.0, 0.0],
                            [0.0, scale_y, 0.0, 0.0],
                            [0.0, 0.0, scale_z, 0.0]))

        affine_shift = np.array(
                            ([1.0, 0.0, 0.0, shift_x],
                            [0.0, 1.0, 0.0, shift_y],
                            [0.0, 0.0, 1.0, 0.0]))

        self.affine_deskew_dict[(self.current_tile_num, self.current_channel_num)] = affine_deskew
        self.affine_scale_dict[(self.current_tile_num, self.current_channel_num)] = affine_scale
        self.affine_shift_dict[(self.current_tile_num, self.current_channel_num)] = affine_shift

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

        # compute necessary inputs to BDV/XML files
        # pyramid subsampling factors xyz
        subsamp = (
                    (1, 1, 1),
                    (2, 2, 2),
                    (4, 4, 4),
                  )
        # chunksize xyz
        blockdim = (
                    (4, 256, 256),
                    (4, 256, 256),
                    (4, 256, 256),
                    (4, 256, 256),
                    (4, 256, 256)
                  )
        filepath = str((Path(self._path) / self._filename).absolute())
        # re-initialize bdv writer for tile/channel list
        # required to dump all datasets in a single bdv file
        bdv_writer = npy2bdv.BdvWriter(
                                filepath,
                                subsamp = subsamp,
                                blockdim = blockdim,
                                compression = self._compression,
                                compression_opts = self.compression_opts,
                                ntiles = len(self.tile_list),
                                nchannels = len(self.channel_list),
                                overwrite = False)
        try:
            # check if tile position already exists
            self.current_tile_num = self.tile_list.index(
                    (self._x_position_mm,
                     self._y_position_mm,
                     self._z_position_mm,
                    )
                )
        except:
            # if does not exist, increment tile number by 1
            self.current_tile_num = len(self.tile_list) + 1
        try:
            # check if tile channel already exists
            self.current_channel_num = self.channel_list.index(self._channel)
        except:
            # if does not exist, increment tile channel by 1
            self.current_channel_num = len(self.channel_list) + 1

        # append all views based to bdv writer
        # this is necessary for bdv writer to have the metadata to write the xml at the end
        # if a view already exists in the bdv file, it will be skipped and not overwritten
        for append_tile, append_channel in self.dataset_dict:
            bdv_writer.append_view(
                                    stack = None,
                                    virtual_stack_dim = (self._frame_count_px,
                                                         self._row_count_px,
                                                         self._column_count_px),
                                    tile = append_tile,
                                    channel = append_channel,
                                    voxel_size_xyz = self.voxel_size_dict[(append_tile, append_channel)],
                                    voxel_units = 'um')

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
            # Write substack of data to BDV file at correct z position
            # current_tile_num and current_channel_num ensure it writes to the correct location
            bdv_writer.append_substack(
                                frames,
                                z_start = chunk_num*CHUNK_COUNT_PX,
                                tile = self.current_tile_num,
                                channel = self.current_channel_num)
            frames = None
            logger.warning(f"{self._filename}: writing chunk took "
                  f"{perf_counter() - start_time:.3f} [s]")
            shm.close()
            self.done_reading.set()
            # NEED TO USE SHARED VALUE HERE
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

        ### write xml file
        bdv_writer.write_xml()

        for append_tile, append_channel in self.affine_deskew_dict:
            bdv_writer.append_affine(m_affine = self.affine_deskew_dict[(append_tile, append_channel)],
                                    name_affine = 'deskew',
                                    tile = append_tile,
                                    channel = append_channel)

        for append_tile, append_channel in self.affine_scale_dict:
            bdv_writer.append_affine(m_affine = self.affine_scale_dict[(append_tile, append_channel)],
                                    name_affine = 'scale',
                                    tile = append_tile,
                                    channel = append_channel)

        for append_tile, append_channel in self.affine_shift_dict:
            bdv_writer.append_affine(m_affine = self.affine_shift_dict[(append_tile, append_channel)],
                                    name_affine = 'shift',
                                    tile = append_tile,
                                    channel = append_channel)
        bdv_writer.close()

    def wait_to_finish(self):
        self.log.info(f"{self._filename}: waiting to finish.")
        self.p.join()
        # log the finished writer %
        self.signal_progress_percent

    def delete_files(self):
        filepath = str((self._path / Path(f"{self._filename}")).absolute())
        xmlpath = str((self._path / Path(f"{self._filename}")).absolute()).replace('h5', 'xml')
        os.remove(filepath)
        os.remove(xmlpath)