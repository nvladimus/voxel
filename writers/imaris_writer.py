import numpy as np
import logging
import multiprocessing
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
    "None":  pw.eCompressionAlgorithmShuffleLZ4,
    "LZ4Shuffle": pw.eCompressionAlgorithmNone,
}

DATA_TYPES = {
    "uint8":  "uint8",
    "uint16": "uint16",
}


class ImarisProgressChecker(pw.CallbackClass):
    """Class for tracking progress of an active ImarisWriter disk-writing
    operation."""

    def __init__(self, stack_name):
        self.stack_name = stack_name
        self.progress = 0  # a float representing the progress (0 to 1.0).

    def RecordProgress(self, progress, total_bytes_written):
        self.progress = progress

class StackWriter(Process):
    """Class for writing a stack of frames to a file on disk."""

    def __init__(self,
                 image_rows: int, image_columns: int, image_count: int,
                 first_img_centroid_x: float, first_img_centroid_y: float,
                 pixel_x_size_um: float, pixel_y_size_um: float,
                 pixel_z_size_um: float,
                 chunk_dimension_order: tuple, compression_style: str,
                 data_type: str, dest_path: Path, stack_name: str,
                 channel_name: str, viz_color_hex: str):
        """Setup the StackWriter to write a compressed stack of images to disk
        as a compressed Imaris file.

        :param image_rows: image sensor rows.
        :param image_columns: image sensor columns.
        :param image_count: number of images in a stack.
        :param first_img_centroid_x: x centroid of the first tile.
        :param first_img_centroid_y: y centroid of the first tile.
        :param pixel_x_size_um:
        :param pixel_y_size_um:
        :param pixel_z_size_um:
        :param chunk_dimension_order: tuple of lowercase lettered axes denoting
            the dimension order.
        :param compression_style: compression algorithm to use on the images.
        :param data_type: string representation of the image data_type.
        :param dest_path: the filepath to write the image stack to.
        :param stack_name: file name with or without the .ims extension. If the
            .ims extension is not present, it will be appended to the file.
        :param channel_name: name of the channel as it appears in the file.
        :param viz_color_hex: color (as a hex string) for the file signal data.
        """
        super().__init__()
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # Lookups for deducing order.
        self.dim_map = {'x': 0, 'y': 1, 'z': 2, 'c': 3, 't': 4}
        # metadata to create the file.
        self.cols = image_columns
        self.rows = image_rows
        self.img_count = image_count
        self.first_img_centroid_x_um = first_img_centroid_x
        self.first_img_centroid_y_um = first_img_centroid_y
        self.pixel_x_size_um = pixel_x_size_um
        self.pixel_y_size_um = pixel_y_size_um
        self.pixel_z_size_um = pixel_z_size_um
        # metadata to write to the file before closing it.
        self.channel_name = channel_name
        self.chunk_dim_order = chunk_dimension_order
        self.dest_path = dest_path
        self.stack_name = stack_name \
            if stack_name.endswith(".ims") else f"{stack_name}.ims"
        self.hex_color = viz_color_hex
        self.converter = None
        # set chunk size to 64 - empirically tuned
        self.chunk_size = 64
        # set threads to double number of cores
        self.thread_count = 2*multiprocessing.cpu_count()
        # set compression type
        valid = list(COMPRESSION_TYPES.keys())
        if compression_style not in valid:
            raise ValueError("compression type must be one of %r." % valid)
        # set data type
        valid = list(DATA_TYPES.keys())
        if data_type not in valid:
            raise ValueError("data type must be one of %r." % valid)
        self.dtype = DATA_TYPES[data_type]
        # Specs for constructing imaris writer
        image_size = pw.ImageSize(x=self.cols, y=self.rows, z=self.img_count,
                                  c=1, t=1)
        # c = channel, t = time. These fields are unused for now.
        # Note: ImarisWriter performs MUCH faster when the dimension sequence
        #   is arranged: x, y, z, c, t.
        #   It is more efficient to transpose/reshape the data into this
        #   shape beforehand instead of defining an arbitrary
        #   DimensionSequence and passing the chunk data in as-is.
        dimension_sequence = pw.DimensionSequence('x', 'y', 'z', 'c', 't')
        block_size = pw.ImageSize(x=self.cols, y=self.rows, z=self.chunk_size,
                                  c=1, t=1)
        sample_size = pw.ImageSize(x=1, y=1, z=1, c=1, t=1)
        # Create Options object.
        opts = pw.Options()
        opts.mNumberOfThreads = self.thread_count
        opts.mEnableLogProgress = True
        # Limit compression options.
        if self.compression_style == 'lz4':
            opts.mCompressionAlgorithmType = pw.eCompressionAlgorithmShuffleLZ4
        elif self.compression_style.upper() == 'None':
            opts.mCompressionAlgorithmType = pw.eCompressionAlgorithmNone

        application_name = 'PyImarisWriter'
        application_version = '1.0.0'

        filepath = str((self.dest_path/Path(f"{self.stack_name}")).absolute())
        self.converter = \
            pw.ImageConverter(self.dtype, image_size, sample_size,
                              dimension_sequence, block_size, filepath, opts,
                              application_name, application_version,
                              self.callback_class)
        # Specs for reconstructing the shared memory object.
        self._shm_name = Array(c_wchar, 32)  # hidden and exposed via property.
        # This is almost always going to be: (chunk_size, rows, columns).
        chunk_shape_map = {'x': image_columns,
           'y': image_rows,
           'z': chunk_size}
        self.shm_shape = [chunk_shape_map[x] for x in self.chunk_dim_order]
        self.shm_nbytes = \
            int(np.prod(self.shm_shape, dtype=np.int64)*np.dtype(self.dtype).itemsize)
        self.frames = None  # will be replaced with an ndarray from shared mem.
        # Flow control attributes to synchronize inter-process communication.
        self.done_reading = Event()
        self.done_reading.set()  # Set after processing all data in shared mem.
        # Internal flow control attributes to monitor compression progress.
        self.callback_class = ImarisProgressChecker(self.stack_name)

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

    def run(self):
        """Loop to wait for data from a specified location and write it to disk
        as an Imaris file. Close up the file afterwards.

        This function executes when called with the start() method.
        """
        chunk_count = ceil(self.img_count/self.chunk_size)
        for chunk_num in range(chunk_count):
            block_index = pw.ImageSize(x=0, y=0, z=chunk_num, c=0, t=0)
            # Wait for new data.
            while self.done_reading.is_set():
                sleep(0.001)
            # Attach a reference to the data from shared memory.
            shm = SharedMemory(self.shm_name, create=False, size=self.shm_nbytes)
            frames = np.ndarray(self.shm_shape, self.dtype, buffer=shm.buf)
            self.log.info(f"Channel {self.channel_name}: writing chunk "
                  f"{chunk_num+1}/{chunk_count} of size {frames.shape}.")
            start_time = perf_counter()
            dim_order = [self.dim_map[x] for x in self.chunk_dim_order]
            # Put the frames back into x, y, z, c, t order.
            self.converter.CopyBlock(frames.transpose(dim_order), block_index)
            frames = None
            self.log.info(f"Channel {self.channel_name}: writing chunk took "
                  f"{perf_counter() - start_time:.3f}[s].")
            shm.close()
            self.done_reading.set()

    def close(self):
        """Close up the imaris file.

        """        
        # Compute the start/end extremes of the enclosed rectangular solid.
        # (x0, y0, z0) position (in [um]) of the beginning of the first voxel,
        # (xf, yf, zf) position (in [um]) of the end of the last voxel.
        x0 = self.first_img_centroid_x_um - (self.pixel_x_size_um * 0.5 * self.cols)
        y0 = self.first_img_centroid_y_um - (self.pixel_y_size_um * 0.5 * self.rows)
        z0 = 0
        xf = self.first_img_centroid_x_um + (self.pixel_x_size_um * 0.5 * self.cols)
        yf = self.first_img_centroid_y_um + (self.pixel_y_size_um * 0.5 * self.rows)
        zf = z0 + self.img_count * self.pixel_z_size_um

        # Wait for file writing to finish.
        if self.callback_class.progress < 1.0:
            self.log.info(f"Waiting for data writing to complete for "
                  f"channel {self.channel_name}[nm] channel. "
                  f"Current progress is {self.callback_class.progress:.3f}.")
        while self.callback_class.progress < 1.0:
            sleep(1.0)
            self.log.info(f"Waiting for data writing to complete for "
                  f"channel {self.channel_name}[nm] channel."
                  f"Current progress is {self.callback_class.progress:.3f}.")
        self.log.info(f"Channel {self.channel_name}: Writing image extents.")
        image_extents = pw.ImageExtents(-x0, -y0, -z0, -xf, -yf, -zf)
        adjust_color_range = False
        parameters = pw.Parameters()
        parameters.set_channel_name(0, self.channel_name)
        time_infos = [datetime.today()]
        color_infos = [pw.ColorInfo()]
        color_spec = pw.Color(*(*hex2color(self.hex_color), 1.0))
        color_infos[0].set_base_color(color_spec)
        # color_infos[0].set_range(0,200)  # possible to autoexpose through this cmd.

        self.converter.Finish(image_extents, parameters, time_infos,
                              color_infos, adjust_color_range)
        self.converter.Destroy()
        self.log.info(f"Channel {self.channel_name}: stack compression complete.")