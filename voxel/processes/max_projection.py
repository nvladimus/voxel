import array
import logging
import numpy as np
import os
import tifffile
import math
from multiprocessing import Process, Value, Event, Array
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path

class MaxProjection(Process):

    def __init__(self):

        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.new_image = Event()
        self.new_image.clear()
        self._column_count_px = None
        self._row_count_px = None
        self._frame_count_px = None
        self._projection_count_px = None
        self._path = None
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
    def path(self, path: Path):
        if os.path.isdir(path):
                self._path = path
        else:
            raise ValueError("%r is not a valid path." % path)
        self.log.info(f'setting path to: {path}')

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self._filename = filename \
            if filename.endswith(".tiff") else f"{filename}.tiff"
        self.log.info(f'setting filename to: {filename}')

    def prepare(self, shm_name):
        self.shm_shape = (self._row_count_px, self._column_count_px)
        # Create attributes to open shared memory in run function
        self.shm = SharedMemory(shm_name, create=False)
        self.latest_img = np.ndarray(self.shm_shape, self._data_type, buffer=self.shm.buf)

    def run(self):
        frame_index = 0
        # Build mips. Assume frames increment sequentially in z.

        # Create XY, YZ, ZX placeholder images.
        self.mip_xy = np.zeros((self._row_count_px, self._column_count_px), dtype=self._data_type)
        self.mip_xz = np.zeros((self._frame_count_px, self._row_count_px), dtype=self._data_type)
        self.mip_yz = np.zeros((self._column_count_px, self._frame_count_px), dtype=self._data_type)

        chunk_count = math.ceil(self._frame_count_px / self._projection_count_px)

        while frame_index < self._frame_count_px:
            chunk_index = frame_index % self._projection_count_px
            # max project latest image
            if self.new_image.is_set():
                self.latest_img = np.ndarray(self.shm_shape, self._data_type, buffer=self.shm.buf)
                self.mip_xy = np.maximum(self.mip_xy, self.latest_img).astype(np.uint16)
                self.mip_yz[:, frame_index] = np.max(self.latest_img, axis=0)
                self.mip_xz[frame_index, :] = np.max(self.latest_img, axis=1)
                # if this projection thickness is complete or end of stack
                if chunk_index == self._projection_count_px - 1 or frame_index == self._frame_count_px - 1:
                    start_index = frame_index - self._projection_count_px + 1
                    end_index = frame_index + 1
                    tifffile.imwrite(self.path / Path(f"mip_xy_z_{start_index}_{end_index}_{self.filename}"), self.mip_xy)
                    # reset the xy mip
                    self.mip_xy = np.zeros((self._row_count_px, self._column_count_px), dtype=self._data_type)
                frame_index += 1
                self.new_image.clear()

        tifffile.imwrite(self.path / Path(f"mip_yz_{self.filename}"), self.mip_yz)
        tifffile.imwrite(self.path / Path(f"mip_xz_{self.filename}"), self.mip_xz)

    def wait_to_finish(self):
        print(f"{self.filename}: waiting to finish.")
        self.join()
        self.log.info(f'saving {self.path}/mip_xy_{self.filename}"')
        self.log.info(f'saving {self.path}/mip_xz_{self.filename}"')
        self.log.info(f'saving {self.path}/mip_yz_{self.filename}"')
