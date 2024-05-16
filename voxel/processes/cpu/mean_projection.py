import array
import logging
import numpy as np
import os
import tifffile
import math
from multiprocessing import Process, Value, Event, Array
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path

class MeanProjection(Process):

    def __init__(self, path: str):

        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if '\\' in path or '/' not in path:
            assert ValueError('path string should only contain / not \\')
        self._path = path
        self.new_image = Event()
        self.new_image.clear()
        self._column_count_px = None
        self._row_count_px = None
        self._frame_count_px = None
        self._projection_count_px = None
        self._filename = None
        self._data_type = None

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
        return self._frame_count_px

    @frame_count_px.setter
    def frame_count_px(self, frame_count_px: int):
        self.log.info(f'setting frame count to: {frame_count_px} [px]')
        self._frame_count_px = frame_count_px

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
        self._filename = filename.replace(".tiff","").replace(".tif", "") \
            if filename.endswith(".tiff") or filename.endswith(".tif") else f"{filename}"
        self.log.info(f'setting filename to: {filename}')

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
        frame_index = 0
        # Build mips. Assume frames increment sequentially in z.

        # Create XY, YZ, ZX placeholder images.
        self.mip_xy = np.zeros((self._row_count_px, self._column_count_px), dtype=self._data_type)
        self.mip_xz = np.zeros((self._frame_count_px, self._row_count_px), dtype=self._data_type)
        self.mip_yz = np.zeros((self._column_count_px, self._frame_count_px), dtype=self._data_type)

        chunk_count = math.ceil(self._frame_count_px / self._projection_count_px)

        while frame_index < self._frame_count_px:
            chunk_index = frame_index % self._projection_count_px
            # minumum project latest image
            if self.new_image.is_set():
                self.latest_img = np.ndarray(self.shm_shape, self._data_type, buffer=self.shm.buf)
                self.mip_xy = np.minimum(self.mip_xy, self.latest_img).astype(np.uint16)
                self.mip_yz[:, frame_index] = np.min(self.latest_img, axis=0)
                self.mip_xz[frame_index, :] = np.min(self.latest_img, axis=1)
                # if this projection thickness is complete or end of stack
                if chunk_index == self._projection_count_px - 1 or frame_index == self._frame_count_px - 1:
                    start_index = int(frame_index - self._projection_count_px + 1)
                    end_index = int(frame_index + 1)
                    tifffile.imwrite(self.path / Path(f"{self.filename}_mean_projection_xy_z_{start_index:06}_{end_index:06}.tiff"), self.mip_xy)
                    # reset the xy mip
                    self.mip_xy = np.zeros((self._row_count_px, self._column_count_px), dtype=self._data_type)
                frame_index += 1
                self.new_image.clear()

        tifffile.imwrite(self.path / Path(f"{self.filename}_mean_projection_yz.tiff"), self.mip_yz)
        tifffile.imwrite(self.path / Path(f"{self.filename}_mean_projection_xz.tiff"), self.mip_xz)

    def wait_to_finish(self):
        self.log.info(f"mean projection {self.filename}: waiting to finish.")
        self.p.join()
        self.log.info(f'saving {self.path}/mean_projection_xy_{self.filename}"')
        self.log.info(f'saving {self.path}/mean_projection_xz_{self.filename}"')
        self.log.info(f'saving {self.path}/mean_projection_yz_{self.filename}"')
