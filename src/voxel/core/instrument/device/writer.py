import time
from abc import abstractmethod
from dataclasses import dataclass
from multiprocessing import Event
from pathlib import Path

import numpy as np
from ome_types.model import OME, Channel, Image, Pixels, Pixels_DimensionOrder, PixelType, UnitsLength

from voxel.core.utils.data_structures.shared_double_buffer import SharedDoubleBuffer
from voxel.core.utils.geometry.vec import Vec2D, Vec3D
from voxel.core.utils.log_config import LoggingSubprocess

from .base import VoxelDevice, VoxelDeviceType


@dataclass
class WriterMetadata:
    """Configuration properties for a frame stack writer."""

    frame_count: int
    frame_shape: Vec2D

    position: Vec3D

    channel_name: str
    channel_idx: int = 0

    voxel_size: Vec3D = Vec3D(1.0, 1.0, 1.0)

    file_name: str


class VoxelWriter(VoxelDevice, LoggingSubprocess):
    """Writer class for voxel data with double buffering"""

    def __init__(self, dir: str, name: str) -> None:
        """Initialize the writer

        :param dir: Directory to write files to
        :type dir: str
        :param name: Name of the writer instance
        :type name: str
        """
        super().__init__(name=name, device_type=VoxelDeviceType.WRITER)

        self.dir = Path(dir)
        if not self.dir.exists():
            self.dir.mkdir(parents=True, exist_ok=True)

        self.dimension_order = Pixels_DimensionOrder.XYZCT
        self.voxel_size_unit = UnitsLength.MICROMETER

        # Synchronization primitives
        self.running_flag = Event()
        self.needs_processing = Event()
        self.timeout = 5

        self.dbl_buf = None

        self.metadata = None
        self.ome: OME | None = None
        self._ome_xml: str | None = None

        self._frame_shape: Vec2D | None = None
        self._frame_count = 0
        self._batch_count = 0
        self._avg_rate = 0

        self._total_data_written = 0
        self._start_time = 0
        self._end_time = 0

    @property
    def dtype(self) -> str:
        """Data type for the written data."""
        return self.pixel_type.numpy_dtype

    @property
    def axes(self) -> str:
        return "".join([axis for axis in self.dimension_order.value if axis in "ZCYX"])[::-1]

    @property
    @abstractmethod
    def batch_size_px(self) -> int:
        """The number of pixels in the z dimension per batch. Determines the size of the buffer.

        :return: Size of batch in Z dimension
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def pixel_type(self) -> PixelType:
        """Pixel type for the written data.

        :return: Pixel type
        :rtype: PixelType
        """
        pass

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize the writer. Called in subprocess after spawning."""
        pass

    @abstractmethod
    def _process_batch(self, batch_data: np.ndarray, batch_count: int) -> None:
        """Process a batch of data with validation and metrics

        :param batch_data: The batch of frame data to process
        :type batch_data: np.ndarray
        :param batch_count: Current batch number (1-based)
        :type batch_count: int
        """
        pass

    @abstractmethod
    def _finalize(self) -> None:
        """Finalize the writer. Called before joining the writer subprocess."""
        pass

    @abstractmethod
    def configure(self, props: WriterMetadata) -> None:
        """Configure the writer with the given properties.
        Ensure that self._props is assigned in this method.
        :param props: Configuration properties
        :type props: WriterProps
        """
        self.metadata = props
        try:
            batch_shape = (self.batch_size_px, self.metadata.frame_shape.y, self.metadata.frame_shape.x)
            self.dbl_buf = SharedDoubleBuffer(batch_shape, self.dtype)
            self.log.info(f"Configured writer with buffer shape: {batch_shape}")
        except Exception as e:
            if self.dbl_buf:
                self.dbl_buf.close_and_unlink()
            raise RuntimeError(f"Failed to configure writer: {e}")

    def start(self) -> None:
        """Start the writer with the given configuration

        :param props: Configuration properties
        :type props: WriterProps
        :raises RuntimeError: If writer fails to start
        """
        if not self.metadata:
            raise RuntimeError("Writer properties not set. Call configure() before starting the writer.")
        try:
            self.ome = self._generate_ome_metadata()
            self._ome_xml = self.ome.to_xml()
            self.running_flag.set()
            self.needs_processing.clear()
            self._frame_count = 0
            self._batch_count = 0
            self._total_data_written = 0
            super().start()
            self.log.debug("Writer started")
        except Exception as e:
            if self.dbl_buf:
                self.dbl_buf.close_and_unlink()
            raise RuntimeError(f"Failed to start writer: {e}")

    def stop(self) -> None:
        """Stop the writer and clean up resources"""

        self._switch_buffers()
        while self.needs_processing.is_set():
            time.sleep(0.001)

        self.running_flag.clear()

        self.log.info(f"Processed {self._frame_count} frames in {self._batch_count} batches")
        self.log.info("Stopping writer")

        self.join()

        if self.dbl_buf:
            self.dbl_buf.close_and_unlink()
            self.dbl_buf = None
        self.log.info("Writer stopped")

    def close(self) -> None:
        """Close the writer and clean up resources"""
        self.stop()
        super().close()

    def _run(self) -> None:
        """Main writer loop"""
        self._initialize()
        self._avg_rate = 0
        self._batch_count = 1
        while self.running_flag.is_set():
            if self.needs_processing.is_set():
                mem_block = self.dbl_buf.mem_blocks[self.dbl_buf.read_mem_block_idx.value]
                shape = (self.dbl_buf.num_frames.value, *self.dbl_buf.shape[1:])
                batch_data = np.ndarray(shape, dtype=self.dtype, buffer=mem_block.buf)

                self._timed_batch_processing(batch_data)

                self.needs_processing.clear()
                self.dbl_buf.num_frames.value = 0
                self._batch_count += 1
                self._frame_count += batch_data.shape[0]
            else:
                time.sleep(0.1)

        self._finalize()

    def add_frame(self, frame: np.ndarray) -> None:
        """Add a frame to the writer

        :param frame: Frame data to add
        :type frame: np.ndarray
        """
        buffer_full = self._frame_count > 0 and self._frame_count % self.batch_size_px == 0

        if buffer_full:
            self._switch_buffers()

        self.dbl_buf.add_frame(frame)
        self._frame_count += 1

    def _switch_buffers(self) -> None:
        """Switch read and write buffers with proper synchronization"""
        # Wait for any ongoing processing to complete
        while self.needs_processing.is_set():
            time.sleep(0.001)

        # Toggle buffers
        self.dbl_buf.toggle_buffers()

        # Signal that new data needs processing
        self.needs_processing.set()

        # Wait for processing to start before continuing
        while not self.needs_processing.is_set():
            time.sleep(0.001)

        self._batch_count += 1

    def _timed_batch_processing(self, batch_data: np.ndarray) -> None:
        """Process a batch of data with timing information

        :param batch_data: The batch of frame data to process
        :type batch_data: np.ndarray
        :param batch_count: Current batch number (1-based)
        :type batch_count: int
        """

        batch_start_time = time.time()
        self._process_batch(batch_data, self._batch_count)
        batch_end_time = time.time()

        time_taken = batch_end_time - batch_start_time
        data_size_mbs = batch_data.nbytes / (1024 * 1024)
        rate_mbps = data_size_mbs / time_taken if time_taken > 0 else 0
        self._avg_rate = (self._avg_rate * (self._batch_count - 1) + rate_mbps) / self._batch_count

        self.log.info(
            f"Batch {self._batch_count}, "
            f"Time: {time_taken:.2f} s, "
            f"Size: {data_size_mbs:.2f} MB, "
            f"Rate: {rate_mbps:.2f} MB/s | "
            f"Avg Rate: {self._avg_rate:.2f} MB/s"
        )

    def _generate_ome_metadata(self) -> OME:
        """Generate OME metadata for the image stack using ome-types."""
        # Create Channel object
        channels = [
            Channel(
                id=f"Channel:0:{i}",
                name=channel_name,
                samples_per_pixel=1,
            )
            for i, channel_name in enumerate(self.metadata.channel_names)
        ]

        # Create Pixels object
        pixels = Pixels(
            id="Pixels:0",
            dimension_order=self.dimension_order,
            type=self.pixel_type,
            size_x=self.metadata.frame_shape.x,
            size_y=self.metadata.frame_shape.y,
            size_z=self.metadata.frame_count,
            size_c=1,
            size_t=1,
            physical_size_x=self.metadata.voxel_size.x,
            physical_size_y=self.metadata.voxel_size.y,
            physical_size_z=self.metadata.voxel_size.z,
            physical_size_x_unit=self.voxel_size_unit,
            physical_size_y_unit=self.voxel_size_unit,
            physical_size_z_unit=self.voxel_size_unit,
            channels=channels,
        )

        # Create Image object
        image = Image(
            id="Image:0",
            name=self.metadata.file_name,
            pixels=pixels,
        )

        # Create OME object
        ome = OME(images=[image])

        return ome
