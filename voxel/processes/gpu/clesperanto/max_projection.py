import array
import logging
import numpy as np
import os
import tifffile
import math
import time
from multiprocessing import Process, Value, Event, Array
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
        self._projection_count_px = None
        self._filename = None
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
    def projection_count_px(self):
        return self._projection_count_px

    @projection_count_px.setter
    def projection_count_px(self, projection_count_px: int):
        self.log.info(f'setting projection count to: {projection_count_px} [px]')
        # projection_count_px = self.frame_count_px / round(self.frame_count_px / projection_count_px)
        # self.log.info(f'adjusting projection count to: {projection_count_px} [px]')
        self._projection_count_px = projection_count_px

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
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self._filename = filename.replace(".tiff","").replace(".tif", "") \
            if filename.endswith(".tiff") or filename.endswith(".tif") else f"{filename}"
        self.log.info(f'setting filename to: {filename}')

    @property
    def buffer_image(self):
        return self._buffer_image

    @buffer_image.setter
    def buffer_image(self, buffer_image: np.ndarray):
        self._buffer_image = buffer_image

    def prepare(self, shm_name):
        self.p = Process(target=self._run)
        self.shm_shape = (self._row_count_px, self._column_count_px)
        # Create attributes to open shared memory in run function
        self.shm = SharedMemory(shm_name, create=False)
        self.latest_img = np.ndarray(self.shm_shape, self._data_type, buffer=self.shm.buf)

    def start(self):
        self.log.info(f"{self._filename}: starting writer.")
        self.p.start()

    def _run(self):
        # cannot pickle cle so import within run function()
        import pyclesperanto as cle

        frame_index = 0
        # Build mips. Assume frames increment sequentially in z.

        # Create XY, YZ, ZX placeholder images.
        self.mip_xy = np.zeros((self._row_count_px, self._column_count_px), dtype=self._data_type)
        self.mip_xz = np.zeros((self._frame_count_px_px, self._row_count_px), dtype=self._data_type)
        self.mip_yz = np.zeros((self._column_count_px, self._frame_count_px_px), dtype=self._data_type)

        chunk_count = math.ceil(self._frame_count_px_px / self._projection_count_px)

        while frame_index < self._frame_count_px_px:
            chunk_index = frame_index % self._projection_count_px
            # max project latest image
            if self.new_image.is_set():
                self.latest_img = np.ndarray(self.shm_shape, self._data_type, buffer=self.shm.buf)
                # move images to gpu
                latest_img = cle.push(self.latest_img)
                mip_xy = cle.push(self.mip_xy)
                # run operation
                new_mip_xy = cle.maximum_images(latest_img,
                                            mip_xy)
                # move image off gpu
                self.mip_xy = cle.pull(new_mip_xy)
                self.mip_yz[:, frame_index] = cle.pull(cle.maximum_y_projection(cle.push(self.latest_img)))
                # maximum_x_projection returns (N,1) array so index [0] to put into self.mip_xz
                self.mip_xz[frame_index, :] = cle.pull(cle.maximum_x_projection(cle.push(self.latest_img)))[0]
                # if this projection thickness is complete or end of stack
                if chunk_index == self._projection_count_px - 1 or frame_index == self._frame_count_px_px - 1:
                    start_index = int(frame_index - self._projection_count_px + 1)
                    end_index = int(frame_index + 1)
                    tifffile.imwrite(Path(self.path, f"{self.filename}_max_projection_xy_z_{start_index:06}_{end_index:06}.tiff"), self.mip_xy)
                    # reset the xy mip
                    self.mip_xy = np.zeros((self._row_count_px, self._column_count_px), dtype=self._data_type)
                frame_index += 1
                self.new_image.clear()

        tifffile.imwrite(Path(self.path, f"{self.filename}_max_projection_yz.tiff"), self.mip_yz)
        tifffile.imwrite(Path(self.path, f"{self.filename}_max_projection_xz.tiff"), self.mip_xz)

    def wait_to_finish(self):
        self.log.info(f"max projection {self.filename}: waiting to finish.")
        self.p.join()
        self.log.info(f'saving {self.path}/max_projection_xy_{self.filename}"')
        self.log.info(f'saving {self.path}/max_projection_xz_{self.filename}"')
        self.log.info(f'saving {self.path}/max_projection_yz_{self.filename}"')
