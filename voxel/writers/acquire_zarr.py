from math import ceil
from pathlib import Path

import os
from acquire import DeviceKind, StorageDimension, DimensionType
from voxel.writers.base import BaseWriter
import acquire

os.environ["ZARR_V3_EXPERIMENTAL_API"] = "1"
os.environ["ZARR_V3_SHARDING"] = "1"

CHUNK_COUNT_PX = 64
DIVISIBLE_FRAME_COUNT_PX = 64

COMPRESSION_TYPES = {
    "none": "ZarrV3",
    "zstdshuffle": "ZarrV3Blosc1ZstdByteShuffle",
    "lz4shuffle": "ZarrV3Blosc1Lz4ByteShuffle"
}


class AcquireZarrWriter(BaseWriter):
    """
    Voxel driver for the Imaris writer.

    Writer will save data to the following location

    path\\acquisition_name\\filename.ims

    :param path: Path for the data writer
    :type path: str
    """

    def __init__(self, path: str):
        super().__init__(path)
        # get global runtime instance, i.e. singleton
        # see __init__.py in acquire-python
        self.runtime = acquire._get_runtime()
        self.acquire_api = self.runtime.get_configuration()

    @property
    def frame_count_px(self):
        """Get the number of frames in the writer.

        :return: Frame number in pixels
        :rtype: int
        """

        return self._frame_count_px

    @frame_count_px.setter
    def frame_count_px(self, frame_count_px: int):
        """Set the number of frames in the writer.

        :param frame_count_px: Frame number in pixels
        :type frame_count_px: int
        """

        self.log.info(f"setting frame count to: {frame_count_px} [px]")
        if frame_count_px % DIVISIBLE_FRAME_COUNT_PX != 0:
            frame_count_px = (
                ceil(frame_count_px / DIVISIBLE_FRAME_COUNT_PX)
                * DIVISIBLE_FRAME_COUNT_PX
            )
            self.log.info(f"adjusting frame count to: {frame_count_px} [px]")
        self._frame_count_px = frame_count_px

    @property
    def chunk_size_x_px(self):
        """Get the chunk count in pixels in x

        :return: Chunk count in pixels in x
        :rtype: int
        """

        return self._chunk_size_x_px

    @chunk_size_x_px.setter
    def chunk_size_x_px(self, chunk_size_x_px: int):
        """Set the chunk count in pixels in x

        :param chunk_size_x_px: Chunk count in pixels in x
        :type chunk_size_x_px: int
        """
        
        self._chunk_size_x_px = chunk_size_x_px
        self.log.info(f"setting chunk size x to: {chunk_size_x_px} [px]")

    @property
    def chunk_size_y_px(self):
        """Get the chunk count in pixels in y

        :return: Chunk count in pixels in y
        :rtype: int
        """

        return self._chunk_size_x_px

    @chunk_size_y_px.setter
    def chunk_size_y_px(self, chunk_size_y_px: int):
        """Set the chunk count in pixels in y

        :param chunk_size_y_px: Chunk count in pixels in y
        :type chunk_size_y_px: int
        """
        
        self._chunk_size_y_px = chunk_size_y_px
        self.log.info(f"setting chunk size y to: {chunk_size_y_px} [px]")

    @property
    def chunk_size_z_px(self):
        """Get the chunk count in pixels in z

        :return: Chunk count in pixels in z
        :rtype: int
        """

        return self._chunk_size_x_px

    @chunk_size_z_px.setter
    def chunk_size_z_px(self, chunk_size_z_px: int):
        """Set the chunk count in pixels in z

        :param chunk_size_z_px: Chunk count in pixels in z
        :type chunk_size_z_px: int
        """
        
        self._chunk_size_z_px = chunk_size_z_px
        self.log.info(f"setting chunk size z to: {chunk_size_z_px} [px]")

    @property
    def shard_size_x_chunks(self):
        """Get the shard size in chunks in x

        :return: Shard size in chunks in x
        :rtype: int
        """

        return self._shard_size_x_chunks

    @shard_size_x_chunks.setter
    def shard_size_x_chunks(self, shard_size_x_chunks: int):
        """Set the shard size in pixels in x

        :param shard_size_x_chunks: Shard size in pixels in x
        :type shard_size_x_chunks: int
        """
        
        self._shard_size_x_chunks = shard_size_x_chunks
        self.log.info(f"setting shard size x to: {shard_size_x_chunks} [chunks]")
    
    @property
    def shard_size_y_chunks(self):
        """Get the shard size in chunks in y

        :return: Shard size in chunks in y
        :rtype: int
        """

        return self._shard_size_y_chunks

    @shard_size_y_chunks.setter
    def shard_size_y_chunks(self, shard_size_y_chunks: int):
        """Set the shard size in chunks in x

        :param shard_size_y_chunks: Shard size in chunks in x
        :type shard_size_y_chunks: int
        """
        
        self._shard_size_y_chunks = shard_size_y_chunks
        self.log.info(f"setting shard size y to: {shard_size_y_chunks} [chunks]")

    @property
    def shard_size_z_chunks(self):
        """Get the shard size in chunks in z

        :return: Shard size in chunks in z
        :rtype: int
        """

        return self._shard_size_z_chunks

    @shard_size_z_chunks.setter
    def shard_size_z_chunks(self, shard_size_z_chunks: int):
        """Set the shard size in chunks in z

        :param shard_size_z_chunks: Shard size in chunks in z
        :type shard_size_z_chunks: int
        """
        
        self._shard_size_z_chunks = shard_size_z_chunks
        self.log.info(f"setting shard size z to: {shard_size_z_chunks} [chunks]")

    @property
    def compression(self):
        """Get the compression codec of the writer.

        :return: Compression codec
        :rtype: str
        """

        return next(
            key
            for key, value in COMPRESSION_TYPES.items()
            if value == self._compression
        )

    @compression.setter
    def compression(self, compression: str):
        """Set the compression codec of the writer.

        :param value: Compression codec
        * **lz4shuffle**
        * **zstdshuffle**
        * **none**
        :type value: str
        """

        valid = list(COMPRESSION_TYPES.keys())
        if compression not in valid:
            raise ValueError("compression type must be one of %r." % valid)
        self.log.info(f"setting compression mode to: {compression}")
        self._compression = COMPRESSION_TYPES[compression]

    @property
    def filename(self):
        """
        The base filename of file writer.

        :return: The base filename
        :rtype: str
        """

        return self._filename

    @filename.setter
    def filename(self, filename: str):
        """
        The base filename of file writer.

        :param value: The base filename
        :type value: str
        """

        self._filename = filename if filename.endswith(".zarr") else f"{filename}.zarr"
        self.log.info(f"setting filename to: {filename}")

    def delete_files(self):
        """
        Delete all files generated by the writer.
        """
        filepath = Path(self._path, self._acquisition_name, self._filename).absolute()
        os.remove(filepath)

    def start(self, frame_count = 2**64 - 1):
        self.acquire_api.video[0].max_frame_count = frame_count
        self.acquire_api = self.runtime.set_configuration(self.acquire_api)
        self.runtime.start()

    def prepare(self):
        """
        Prepare the ZarrV3 writer. Shards can be ragged, i.e. greater than or equal to the frame size in x or y.
        For example:
        frame size x = 14192
        frame size y = 10640
        chunk size x = 128
        chunk size y = 128
        shard chunks x = 111
        shard chunks y = 85
        shard size x = 14208
        shard size y = 10752
        """

        # ensure chunk x shard is larger than x/y dims
        x_array_size_px = self._chunk_size_x_px * self._shard_size_x_chunks
        if x_array_size_px < self._column_count_px:
            raise ValueError(f'x chunk size * x shard size = {x_array_size_px} but frame size x = {self._column_count_px}')
        y_array_size_px = self._chunk_size_y_px * self._shard_size_y_chunks
        if y_array_size_px < self._row_count_px:
            raise ValueError(f'y chunk size * y shard size = {y_array_size_px} but frame size y = {self._row_count_px}')

        self.log.info(f"{self._filename}: intializing writer.")
        filepath = str(Path(self._path, self._acquisition_name, self._filename).absolute())
        device_manager = self.runtime.device_manager()
        self.acquire_api.video[0].storage.identifier = device_manager.select(DeviceKind.Storage, self._compression)
        self.acquire_api.video[0].storage.settings.filename = filepath
        self.acquire_api.video[0].storage.settings.pixel_scale_um = (self._x_voxel_size_um, self._y_voxel_size_um)
        self.acquire_api.video[0].storage.settings.enable_multiscale = False  # not enabled for zarrv3 yet

        x_dimension = StorageDimension()
        x_dimension.name = 'x'
        x_dimension.kind = DimensionType.Space
        x_dimension.array_size_px = self._column_count_px
        x_dimension.chunk_size_px = self._chunk_size_x_px
        x_dimension.shard_size_chunks = self._shard_size_x_chunks

        y_dimension = StorageDimension()
        y_dimension.name = 'y'
        x_dimension.kind = DimensionType.Space
        y_dimension.array_size_px = self._row_count_px
        y_dimension.chunk_size_px = self._chunk_size_y_px
        y_dimension.shard_size_chunks = self._shard_size_y_chunks

        z_dimension = StorageDimension()
        z_dimension.name = 'z'
        x_dimension.kind = DimensionType.Space
        z_dimension.array_size_px = 0  # append dimension must be 0
        z_dimension.chunk_size_px = self._chunk_size_z_px
        z_dimension.shard_size_chunks = self._shard_size_z_chunks

        self.acquire_api.video[0].storage.settings.acquisition_dimensions = [x_dimension, y_dimension, z_dimension]

        self.acquire_api = self.runtime.set_configuration(self.acquire_api)  # set the new configuration
