import array
import logging
import numpy as np
import os
import tifffile
import math
import time
from multiprocessing import Process, Event
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path


class MaxProjection:

    def __init__(self, path: str):

        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._path = Path(path)
        self._column_count_px = None
        self._row_count_px = None
        self._frame_count_px_px = None
        self._x_projection_count_px = None
        self._y_projection_count_px = None
        self._z_projection_count_px = None
        self._filename = None
        self._acquisition_name = Path()
        self._data_type = None
        self.new_image = Event()
        self.new_image.clear()

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
    def frame_count_px(self):
        return self._frame_count_px_px

    @frame_count_px.setter
    def frame_count_px(self, frame_count_px: int):
        self.log.info(f'setting frame count to: {frame_count_px} [px]')
        self._frame_count_px_px = frame_count_px

    @property
    def x_projection_count_px(self):
        return self._x_projection_count_px

    @x_projection_count_px.setter
    def x_projection_count_px(self, x_projection_count_px: int):
        self.log.info(f'setting projection count to: {x_projection_count_px} [px]')
        self._x_projection_count_px = x_projection_count_px

    @property
    def y_projection_count_px(self):
        return self._y_projection_count_px

    @y_projection_count_px.setter
    def y_projection_count_px(self, y_projection_count_px: int):
        self.log.info(f'setting projection count to: {y_projection_count_px} [px]')
        self._y_projection_count_px = y_projection_count_px

    @property
    def z_projection_count_px(self):
        return self._z_projection_count_px

    @z_projection_count_px.setter
    def z_projection_count_px(self, z_projection_count_px: int):
        self.log.info(f'setting projection count to: {z_projection_count_px} [px]')
        self._z_projection_count_px = z_projection_count_px

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
    def path(self, path: str):
        self._path = Path(path)
        self.log.info(f'setting path to: {path}')

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
        self._filename = filename.replace(".tiff", "").replace(".tif", "") \
            if filename.endswith(".tiff") or filename.endswith(".tif") else f"{filename}"
        self.log.info(f'setting filename to: {filename}')

    def prepare(self, shm_name):
        self.p = Process(target=self._run)
        self.shm_shape = (self._row_count_px, self._column_count_px)
        # create attributes to open shared memory in run function
        self.shm = SharedMemory(shm_name, create=False)
        self.latest_img = np.ndarray(self.shm_shape, self._data_type, buffer=self.shm.buf)

    def start(self):
        self.log.info(f"{self._filename}: starting writer.")
        self.p.start()

    def _run(self):

        # check if projection counts were set
        # if not, set to max possible values based on tile
        if self._x_projection_count_px == None:
            x_projection = False
        else:
            x_projection = True
            if self._x_projection_count_px < 0 or self._x_projection_count_px > self._column_count_px:
                raise ValueError(f'x projection must be > 0 and < {self._column_count_px}')
            x_index_list = np.arange(0, self._column_count_px, self._x_projection_count_px)
            if self._column_count_px not in x_index_list:
                x_index_list = np.append(x_index_list, self._column_count_px)
            self.mip_yz = np.zeros((self._frame_count_px_px, self._row_count_px, len(x_index_list)), dtype=self._data_type)
        if self._y_projection_count_px == None:
            y_projection = False
        else:
            y_projection = True
            if self._y_projection_count_px < 0 or self._y_projection_count_px > self._row_count_px:
                raise ValueError(f'y projection must be > 0 and < {self._row_count_px}')
            y_index_list = np.arange(0, self._row_count_px, self._y_projection_count_px)
            if self._row_count_px not in y_index_list:
                y_index_list = np.append(y_index_list, self._row_count_px)
            self.mip_xz = np.zeros((self._frame_count_px_px, self._column_count_px, len(y_index_list)), dtype=self._data_type)
        if self._z_projection_count_px == None:
            z_projection = False
        else:
            z_projection = True
            if self._z_projection_count_px < 0 or self._z_projection_count_px > self._frame_count_px_px:
                raise ValueError(f'z projection must be > 0 and < {self._frame_count_px}')
            self.mip_xy = np.zeros((self._row_count_px, self._column_count_px), dtype=self._data_type)

        frame_index = 0
        start_index = 0

        while frame_index < self._frame_count_px_px:
            chunk_index = frame_index % self._z_projection_count_px
            # max project latest image
            if self.new_image.is_set():
                self.latest_img = np.ndarray(self.shm_shape, self._data_type, buffer=self.shm.buf)
                if z_projection:
                    self.mip_xy = np.maximum(self.mip_xy, self.latest_img).astype(np.uint16)
                    # if this projection thickness is complete or end of stack
                    if chunk_index == self._z_projection_count_px - 1 or frame_index == self._frame_count_px_px - 1:
                        end_index = int(frame_index + 1)
                        self.log.info(f'saving {self.filename}_max_projection_xy_z_{start_index:06}_{end_index:06}.tiff')
                        tifffile.imwrite(
                            Path(self.path, self._acquisition_name, f"{self.filename}_max_projection_xy_z_{start_index:06}_{end_index:06}.tiff"),
                            self.mip_xy)
                        # reset the xy mip
                        self.mip_xy = np.zeros((self._row_count_px, self._column_count_px), dtype=self._data_type)
                        # set next start index to previous end index
                        start_index = end_index
                if x_projection:
                    for i in range(0, len(x_index_list)-1):
                        self.mip_yz[frame_index, :, i] = np.max(self.latest_img[:, x_index_list[i]:x_index_list[i+1]], axis=1)
                if y_projection:
                    for i in range(0, len(y_index_list)-1):
                        self.mip_xz[frame_index, :, i] = np.max(self.latest_img[y_index_list[i]:y_index_list[i+1], :], axis=0)
                frame_index += 1
                self.new_image.clear()
        if x_projection:
            for i in range(0, len(x_index_list)-1):
                start_index = x_index_list[i]
                end_index = x_index_list[i+1]
                self.log.info(f'saving {self.filename}_max_projection_yz_x_{start_index:06}_{end_index:06}.tiff')
                tifffile.imwrite(Path(self.path, self._acquisition_name, f"{self.filename}_max_projection_yz_x_{start_index:06}_{end_index:06}.tiff"), self.mip_yz[:, :, i])
        if y_projection:
            for i in range(0, len(y_index_list)-1):
                start_index = y_index_list[i]
                end_index = y_index_list[i+1]
                self.log.info(f'saving {self.filename}_max_projection_xz_y_{start_index:06}_{end_index:06}.tiff')
                tifffile.imwrite(Path(self.path, self._acquisition_name, f"{self.filename}_max_projection_xz_y_{start_index:06}_{end_index:06}.tiff"), self.mip_xz[:, :, i])

    def wait_to_finish(self):
        self.log.info(f"max projection {self.filename}: waiting to finish.")
        self.p.join()
