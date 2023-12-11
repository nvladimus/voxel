import numpy as np
import logging
import multiprocessing
import re
import os
from multiprocessing import Process, Array, Event
from multiprocessing.shared_memory import SharedMemory
from ctypes import c_wchar
from PyImarisWriter import PyImarisWriter as pw
from pathlib import Path
from datetime import datetime
from matplotlib.colors import hex2color
from time import sleep, perf_counter
from math import ceil

COMPRESSION_TYPES = {
    "none":  pw.eCompressionAlgorithmShuffleLZ4,
    "lz4shuffle": pw.eCompressionAlgorithmNone,
}

DATA_TYPES = {
    "uint8":  "uint8",
    "uint16": "uint16",
}

class ImarisProgressChecker(pw.CallbackClass):
    """Class for tracking progress of an active ImarisWriter disk-writing
    operation."""

    def __init__(self):
        self.progress = 0  # a float representing the progress (0 to 1.0).

    def RecordProgress(self, progress, total_bytes_written):
        self.progress = progress

class Writer(Process):

    def __init__(self):
 
        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # Opinioated decision on chunking dimension order
        self.chunk_dim_order = ('z', 'y', 'x')
        # Flow control attributes to synchronize inter-process communication.
        self.done_reading = Event()
        self.done_reading.set()  # Set after processing all data in shared mem.
        # Internal flow control attributes to monitor compression progress.
        self.callback_class = ImarisProgressChecker()

    @property
    def x_voxel_size(self):
        return self.pixel_x_size_um

    @x_voxel_size.setter
    def x_voxel_size(self, x_voxel_size: float):
        self.pixel_x_size_um = x_voxel_size

    @property
    def y_voxel_size(self):
        return self.pixel_y_size_um

    @y_voxel_size.setter
    def y_voxel_size(self, y_voxel_size: float):
        self.pixel_y_size_um = y_voxel_size

    @property
    def z_voxel_size(self):
        return self.pixel_z_size_um

    @z_voxel_size.setter
    def z_voxel_size(self, z_voxel_size: float):
        self.pixel_z_size_um = z_voxel_size

    @property
    def x_pos(self):
        return self.first_img_centroid_x_um

    @x_pos.setter
    def x_pos(self, x_pos: float):
        self.first_img_centroid_x_um = x_pos

    @property
    def y_pos(self):
        return self.first_img_centroid_y_um

    @y_pos.setter
    def y_pos(self, y_pos: float):
        self.first_img_centroid_y_um = y_pos

    @property
    def frame_count(self):
        return self.img_count

    @frame_count.setter
    def frame_count(self, frame_count: int):
        self.img_count = frame_count

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
    def chunk_count(self):
        return self.chunk_size

    @chunk_count.setter
    def chunk_count(self, chunk_count: int):
        self.chunk_size = chunk_count

    @property
    def compression(self):
        return next(key for key, value in COMPRESSION_TYPES.items() if value == self.compression_style)

    @compression.setter
    def compression(self, compression: str):
        valid = list(COMPRESSION_TYPES.keys())
        if compression not in valid:
            raise ValueError("compression type must be one of %r." % valid)
        self.compression_style = compression

    @property
    def dtype(self):
        return next(key for key, value in DATA_TYPES.items() if value == self.data_type)

    @dtype.setter
    def dtype(self, dtype: str):
        valid = list(DATA_TYPES.keys())
        if dtype not in valid:
            raise ValueError("data type must be one of %r." % valid)
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
            if filename.endswith(".ims") else f"{filename}.ims"

    @property
    def channel(self):
        return self.channel_name

    @channel.setter
    def channel(self, channel: str):
        self.channel_name = channel

    @property
    def color(self):
        return self.viz_color_hex

    @color.setter
    def color(self, color: str):
        if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
            self.viz_color_hex = color
        else:
            raise ValueError("%r is not a valid hex color code." % color)

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

    def buffer(self):
        # Specs for reconstructing the shared memory object.
        self._shm_name = Array(c_wchar, 32)  # hidden and exposed via property.
        # This is almost always going to be: (chunk_size, rows, columns).
        chunk_shape_map = {'x': self.cols,
           'y': self.rows,
           'z': self.chunk_size}
        self.shm_shape = [chunk_shape_map[x] for x in self.chunk_dim_order]
        self.shm_nbytes = \
            int(np.prod(self.shm_shape, dtype=np.int64)*np.dtype(DATA_TYPES[self.dtype]).itemsize)

    def run(self):
        """Loop to wait for data from a specified location and write it to disk
        as an Imaris file. Close up the file afterwards.

        This function executes when called with the start() method.
        """
        print(f"{self.stack_name}: intializing writer.")
        self.application_name = 'PyImarisWriter'
        self.application_version = '1.0.0'
        # voxel size metadata to create the converter
        self.image_size = pw.ImageSize(x=self.cols, y=self.rows, z=self.img_count,
                          c=1, t=1)
        self.block_size = pw.ImageSize(x=self.cols, y=self.rows, z=self.chunk_size,
                                  c=1, t=1)
        self.sample_size = pw.ImageSize(x=1, y=1, z=1, c=1, t=1)
        # compute the start/end extremes of the enclosed rectangular solid.
        # (x0, y0, z0) position (in [um]) of the beginning of the first voxel,
        # (xf, yf, zf) position (in [um]) of the end of the last voxel.
        x0 = self.first_img_centroid_x_um - (self.pixel_x_size_um * 0.5 * self.cols)
        y0 = self.first_img_centroid_y_um - (self.pixel_y_size_um * 0.5 * self.rows)
        z0 = 0
        xf = self.first_img_centroid_x_um + (self.pixel_x_size_um * 0.5 * self.cols)
        yf = self.first_img_centroid_y_um + (self.pixel_y_size_um * 0.5 * self.rows)
        zf = z0 + self.img_count * self.pixel_z_size_um
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
        self.parameters.set_channel_name(0, self.channel_name)
        # create options object
        self.opts = pw.Options()
        self.opts.mEnableLogProgress = True
        # set threads to double number of cores
        self.thread_count = 2*multiprocessing.cpu_count()
        self.opts.mNumberOfThreads = self.thread_count
        # set compression type
        if self.compression_style == 'lz4shuffle':
            self.opts.mCompressionAlgorithmType = pw.eCompressionAlgorithmShuffleLZ4
        elif self.compression_style == 'none':
            self.opts.mCompressionAlgorithmType = pw.eCompressionAlgorithmNone
        # color parameters
        self.adjust_color_range = False
        self.color_infos = [pw.ColorInfo()]
        self.color_infos[0].set_base_color(pw.Color(*(*hex2color(self.viz_color_hex), 1.0)))
        # date time parameters
        self.time_infos = [datetime.today()]

        print(f"{self.stack_name}: starting writer.")
        filepath = str((self.dest_path/Path(f"{self.stack_name}")).absolute())
        self.converter = \
            pw.ImageConverter(DATA_TYPES[self.dtype], self.image_size, self.sample_size,
                              self.dimension_sequence, self.block_size, filepath, 
                              self.opts, self.application_name,
                              self.application_version, self.callback_class)
        chunk_count = ceil(self.img_count/self.chunk_size)
        for chunk_num in range(chunk_count):
            block_index = pw.ImageSize(x=0, y=0, z=chunk_num, c=0, t=0)
            # Wait for new data.
            while self.done_reading.is_set():
                sleep(0.001)
            # Attach a reference to the data from shared memory.
            shm = SharedMemory(self.shm_name, create=False, size=self.shm_nbytes)
            frames = np.ndarray(self.shm_shape, DATA_TYPES[self.dtype], buffer=shm.buf)
            print(f"{self.stack_name}: writing chunk "
                  f"{chunk_num+1}/{chunk_count} of size {frames.shape}.")
            start_time = perf_counter()
            dim_order = [self.dim_map[x] for x in self.chunk_dim_order]
            # Put the frames back into x, y, z, c, t order.
            self.converter.CopyBlock(frames.transpose(dim_order), block_index)
            frames = None
            print(f"{self.stack_name}: writing chunk took "
                  f"{perf_counter() - start_time:.3f}[s].")
            shm.close()
            self.done_reading.set()

        # Wait for file writing to finish.
        if self.callback_class.progress < 1.0:
            print(f"waiting for data writing to complete for "
                  f"{self.stack_name}. "
                  f"current progress is {self.callback_class.progress:.3f}.")
        while self.callback_class.progress < 1.0:
            sleep(1.0)
            print(f"waiting for data writing to complete for "
                  f"{self.stack_name}. "
                  f"current progress is {self.callback_class.progress:.3f}.")

        self.converter.Finish(self.image_extents, self.parameters, self.time_infos,
                              self.color_infos, self.adjust_color_range)
        self.converter.Destroy()
        print(f"{self.stack_name}: stack writing complete.")

    def wait_to_finish(self):
        print(f"{self.stack_name}: waiting to finish.")
        self.join()