import logging
import time
from abc import abstractmethod
from dataclasses import dataclass
from multiprocessing import Event
from pathlib import Path

import numpy as np
from ome_types.model import OME, Channel, Image, Pixels, Pixels_DimensionOrder, PixelType, UnitsLength

from voxel.core.instrument.io.data_structures.shared_double_buffer import SharedDoubleBuffer
from voxel.core.utils.geometry.vec import Vec2D, Vec3D
from voxel.core.utils.log_config import LoggingSubprocess


@dataclass
class WriterMetadata:
    """Configuration properties for a frame stack writer."""

    frame_count: int
    frame_shape: Vec2D

    position: Vec3D
    file_name: str

    channel_names: list = None

    voxel_size: Vec3D = Vec3D(1.0, 1.0, 1.0)


class VoxelWriter(LoggingSubprocess):
    """Writer class for voxel data with double buffering"""

    def __init__(self, dir: str, name: str) -> None:
        """Initialize the writer

        :param dir: Directory to write files to
        :type dir: str
        :param name: Name of the writer instance
        :type name: str
        """
        super().__init__(name)

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
    def size_c(self) -> int:
        return len(self.metadata.channel_names) if self.metadata.channel_names else 1

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


class SimpleWriter(VoxelWriter):
    """Simple writer class for testing purposes"""

    @property
    def pixel_type(self) -> PixelType:
        return PixelType.UINT16

    @property
    def batch_size_px(self) -> int:
        return 64

    def configure(self, props: WriterMetadata) -> None:
        super().configure(props)
        self.log.info(
            f"Configured writer with {self.metadata.frame_count} frames "
            f"of shape: {self.metadata.frame_shape.x}x{self.metadata.frame_shape.y}"
        )

    def _initialize(self) -> None:
        self.log.info(f"Initialized. Expecting {self.metadata.frame_count} frames in {self.batch_size_px} px batches")

    def _process_batch(self, batch_data, batch_count) -> None:
        num_frames = batch_data.shape[0]
        start_frame = (batch_count - 1) * self.batch_size_px
        expected_frames = range(start_frame, start_frame + num_frames)

        frame_errors = []
        for i, frame_idx in enumerate(expected_frames):
            frame = batch_data[i]
            expected_value = frame_idx
            if not np.all(frame == expected_value):
                actual_vals = np.unique(frame)
                frame_errors.append(f"Frame {frame_idx}: Expected {expected_value}, found values {actual_vals}")

        stats = {
            "batch_number": batch_count,
            "frames_processed": num_frames,
            "frame_range": f"{start_frame}-{start_frame + num_frames - 1}",
            "min_value": np.min(batch_data),
            "max_value": np.max(batch_data),
            "mean_value": np.mean(batch_data),
            "validation_errors": len(frame_errors),
        }

        self.log.info(
            f"Batch {stats['batch_number']:2d} | "
            f"({stats['frame_range']}) {stats['frames_processed']:3d} frames | "
            f"{stats['min_value']:3d} - {stats['mean_value']:.1f} - {stats['max_value']:3d} | "
            f"Errors: {stats['validation_errors']}"
        )

        if frame_errors:
            self.log.debug("Validation errors:\n" + "\n".join(frame_errors))

    def _finalize(self) -> None:
        self.log.info("Finalized...")


def generate_frames(frame_count, frame_shape, batch_size_px, dtype, logger: logging.Logger = None):
    """Generate test frames with sequential values."""
    batch_idx = 0
    for frame_z in range(frame_count):
        start_time = time.time()
        # Fill frame with the current frame index
        frame = np.full((frame_shape.y, frame_shape.x), frame_z, dtype=dtype)
        end_time = time.time()
        time_taken = end_time - start_time
        if logger:
            logger.debug(f"Frame {frame_z} generated in {time_taken:.6f} seconds")
        # Log frame generation for debugging
        if frame_z % batch_size_px == 0:
            batch_idx += 1
        yield frame


def generate_checkered_frames(frame_count, frame_shape, dtype, logger: logging.Logger = None):
    """Generate test frames with checkerboard patterns."""
    min_tile_size = 4
    max_tile_size = min(frame_shape.x, frame_shape.y) // 4

    tile_sizes = np.linspace(min_tile_size, max_tile_size, num=frame_count, dtype=int)

    # Precompute meshgrid indices
    y_indices = np.arange(frame_shape.y)
    x_indices = np.arange(frame_shape.x)
    xv, yv = np.meshgrid(x_indices, y_indices)

    for frame_z in range(frame_count):
        start_time = time.time()
        tile_size = tile_sizes[frame_z]

        # Compute the checkerboard pattern directly
        checkerboard = ((xv // tile_size + yv // tile_size) % 2).astype(dtype)

        # Scale to full intensity range
        frame = checkerboard * 255

        end_time = time.time()
        time_taken = end_time - start_time
        if logger:
            logger.debug(f"Frame {frame_z} generated in {time_taken:.6f} seconds")

        yield frame


def generate_spiral_frames(frame_count, frame_shape, dtype, logger: logging.Logger = None):
    """Generate frames with spiral patterns."""
    min_tile_size = 2
    max_tile_size = min(frame_shape.x, frame_shape.y) // 12

    tile_sizes = np.linspace(min_tile_size, max_tile_size, num=frame_count, dtype=int)

    # Create indices centered on the frame (precomputed)
    y_indices = np.arange(frame_shape.y) - frame_shape.y // 2
    x_indices = np.arange(frame_shape.x) - frame_shape.x // 2
    xv, yv = np.meshgrid(x_indices, y_indices)

    # Precompute distance from the center
    distance = np.sqrt(xv**2 + yv**2)

    for frame_z in range(frame_count):
        start_time = time.time()
        tile_size = tile_sizes[frame_z]

        # Create expanding pattern
        pattern = ((distance // tile_size) % 2).astype(dtype)

        # Scale to full intensity range
        frame = pattern * 255

        end_time = time.time()
        time_taken = end_time - start_time
        if logger:
            logger.debug(f"Frame {frame_z} generated in {time_taken:.6f} seconds")

        yield frame


def test_writer():
    """Test the writer with power of 2 dimensions"""

    writer = SimpleWriter("test", "test_writer")

    NUM_BATCHES = 2
    frame_shape = Vec2D(4096, 4096)
    frame_count = (writer.batch_size_px * NUM_BATCHES) - 40
    props = WriterMetadata(
        frame_count=frame_count,
        frame_shape=frame_shape,
        position=Vec3D(0, 0, 0),
        file_name="test_file_power_of_2",
    )

    writer.configure(props)
    writer.log.info(f"Expecting: {frame_count} frames of {frame_shape.x}x{frame_shape.y} in {NUM_BATCHES} batche(s)")
    writer.start()

    try:
        for frame in generate_frames(frame_count, frame_shape, writer.batch_size_px, writer.dtype, writer.log):
            writer.add_frame(frame)

    except Exception as e:
        writer.log.error(f"Test failed: {e}")
    finally:
        writer.stop()


if __name__ == "__main__":
    from voxel.core.utils.log_config import setup_logging

    setup_logging()
    test_writer()
