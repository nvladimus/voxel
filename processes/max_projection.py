import array
import logging
import numpy as np
import os
import tifffile
from multiprocessing import Process, Value, Event, Array
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path

class Processor(Process):

    def __init__(self):

        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.new_image = Event()
        self.new_image.clear()

    @property
    def column_count(self):
        return self.cols

    @column_count.setter
    def column_count(self, column_count: int):
        self.cols = column_count

    @property
    def row_count(self):
        return self.rows

    @row_count.setter
    def row_count(self, row_count: int):
        self.rows = row_count

    @property
    def frame_count(self):
        return self.img_count

    @frame_count.setter
    def frame_count(self, frame_count: int):
        self.img_count = frame_count

    @property
    def dtype(self):
        return self.data_type

    @dtype.setter
    def dtype(self, dtype: np.unsignedinteger):
        self.data_type = dtype

    @property
    def path(self):
        return self.dest_path

    @path.setter
    def path(self, path: Path):
        if os.path.isdir(path):
                self.dest_path = path
        else:
            raise ValueError("%r is not a valid path." % path)

    @property
    def filename(self):
        return self.stack_name

    @filename.setter
    def filename(self, filename: str):
        self.stack_name = filename \
            if filename.endswith(".tiff") else f"{filename}.tiff"

    def prepare(self, shm_name):
        self.shm_shape = (self.rows, self.cols)
        # Create XY, YZ, ZX placeholder images.
        self.mip_xy = np.zeros((self.rows, self.cols), dtype=self.dtype)
        self.mip_xz = np.zeros((self.frame_count, self.rows), dtype=self.dtype)
        self.mip_yz = np.zeros((self.cols, self.frame_count), dtype=self.dtype)

        # Create attributes to open shared memory in run function
        self.shm = SharedMemory(shm_name, create=False)
        self.latest_img = np.ndarray(self.shm_shape, self.dtype, buffer=self.shm.buf)

    def run(self):
        frame_index = 0
        # Build mips. Assume frames increment sequentially in z.
        while frame_index < self.frame_count:
            if self.new_image.is_set():
                self.latest_img = np.ndarray(self.shm_shape, self.data_type, buffer=self.shm.buf)
                print(np.max(self.latest_img[:]))
                self.mip_xy = np.maximum(self.mip_xy, self.latest_img).astype(np.uint16)
                self.mip_yz[:, frame_index] = np.max(self.latest_img, axis=0)
                self.mip_xz[frame_index, :] = np.max(self.latest_img, axis=1)
                frame_index += 1
                self.new_image.clear()

        tifffile.imwrite(self.path / Path(f"mip_xy_{self.filename}.tiff"), self.mip_xy)
        tifffile.imwrite(self.path / Path(f"mip_yz_{self.filename}.tiff"), self.mip_yz)
        tifffile.imwrite(self.path / Path(f"mip_xz_{self.filename}.tiff"), self.mip_xz)

    def wait_to_finish(self):
        print(f"{self.filename}: waiting to finish.")
        self.join()
