from abc import abstractmethod
from dataclasses import dataclass
from multiprocessing import Event
from pathlib import Path
from time import sleep
from cycler import V
import numpy as np

from voxel.core.instrument.io.data_structures.shared_double_buffer import SharedDoubleBuffer
from voxel.core.utils.geometry.vec import Vec2D, Vec3D
from voxel.core.utils.logging import LoggingSubprocess


@dataclass
class WriterProps:
    """Configuration properties for a frame stack writer."""

    frame_count: int
    frame_shape: Vec2D

    position: Vec3D
    file_name: str


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

        # Synchronization primitives
        self.running_flag = Event()
        self.needs_processing = Event()
        self.timeout = 5

        self.dbl_buf = None

        self._props = None
        self._frame_shape: Vec2D | None = None
        self._frame_count = 0
        self._batch_count = 0

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
    def data_type(self) -> np.dtype:
        """Data type for the written data.

        :return: Data type
        :rtype: np.dtype
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
    def configure(self, props: WriterProps) -> None:
        """Configure the writer with the given properties.
        Ensure that self._props is assigned in this method.
        :param props: Configuration properties
        :type props: WriterProps
        """
        self._props = props
        try:
            batch_shape = (self.batch_size_px, self._props.frame_shape.y, self._props.frame_shape.x)
            self.dbl_buf = SharedDoubleBuffer(batch_shape, self.data_type_str)
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
        if not self._props:
            raise RuntimeError("Writer properties not set. Call configure() before starting the writer.")
        try:
            self.running_flag.set()
            self.needs_processing.clear()
            self._frame_count = 0
            self._batch_count = 0
            super().start()
            self.log.debug("Writer started")
        except Exception as e:
            if self.dbl_buf:
                self.dbl_buf.close_and_unlink()
            raise RuntimeError(f"Failed to start writer: {e}")

    def stop(self) -> None:
        """Stop the writer and clean up resources"""

        self._switch_buffers()

        # Wait for final processing to complete
        while self.needs_processing.is_set():
            sleep(0.001)

        self.log.info(f"Processed {self._frame_count} frames in {self._batch_count} batches")
        self.log.info("Stopping writer")
        self.running_flag.clear()

        self.join()

        if self.dbl_buf:
            self.dbl_buf.close_and_unlink()
            self.dbl_buf = None
        self.log.info("Writer stopped")

    def _run(self) -> None:
        """Main writer loop"""
        self._initialize()
        try:
            batch_count = 1
            while self.running_flag.is_set() or self.needs_processing.is_set():
                if self.needs_processing.is_set():
                    try:
                        mem_block = self.dbl_buf.mem_blocks[self.dbl_buf.read_mem_block_idx.value]
                        batch_data = np.ndarray(self.dbl_buf.shape, dtype=self.data_type, buffer=mem_block.buf)
                        self._process_batch(batch_data, batch_count)
                    except Exception as e:
                        self.log.error(f"Error processing batch: {e}")
                    finally:
                        self.needs_processing.clear()
                        batch_count += 1
                else:
                    sleep(0.1)
        finally:
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
            sleep(0.001)

        # Toggle buffers
        self.dbl_buf.toggle_buffers()

        # Signal that new data needs processing
        self.needs_processing.set()

        # Wait for processing to start before continuing
        while not self.needs_processing.is_set():
            sleep(0.001)

        self._batch_count += 1

    @property
    def data_type_str(self) -> str:
        return np.dtype(self.data_type).name


class SimpleWriter(VoxelWriter):
    """Simple writer class for testing purposes"""

    @property
    def data_type(self) -> np.dtype:
        return np.uint16

    @property
    def batch_size_px(self) -> int:
        return 64

    def configure(self, props: WriterProps) -> None:
        super().configure(props)
        self.log.info(
            f"Configured writer with {self._props.frame_count} frames "
            f"of shape: {self._props.frame_shape.x}x{self._props.frame_shape.y}"
        )

    def _initialize(self) -> None:
        self.log.info(f"Initialized. Expecting {self._props.frame_count} frames in {self.batch_size_px} px batches")

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


def generate_frames(frame_count, frame_shape, batch_size_px, data_type):
    """Generate test frames with sequential values"""
    batch_idx = 0
    for frame_z in range(frame_count):
        # Fill frame with the current frame index
        frame = np.full((frame_shape.y, frame_shape.x), frame_z, dtype=data_type)

        # Log frame generation for debugging
        if frame_z % batch_size_px == 0:
            batch_idx += 1

        yield frame


def test_writer():
    """Test the writer with power of 2 dimensions"""

    writer = SimpleWriter("test", "test_writer")

    NUM_BATCHES = 10
    frame_shape = Vec2D(4096, 4096)
    frame_count = writer.batch_size_px * NUM_BATCHES
    props = WriterProps(
        frame_count=frame_count,
        frame_shape=frame_shape,
        position=Vec3D(0, 0, 0),
        file_name="test_file_power_of_2",
    )

    writer.configure(props)
    writer.log.info(f"Expecting: {frame_count} frames of {frame_shape.x}x{frame_shape.y} in {NUM_BATCHES} batche(s)")
    writer.start()

    try:
        for frame in generate_frames(frame_count, frame_shape, writer.batch_size_px, writer.data_type):
            writer.add_frame(frame)

    except Exception as e:
        writer.log.error(f"Test failed: {e}")
    finally:
        writer.stop()


if __name__ == "__main__":
    from voxel.core.utils.logging import run_with_logging

    run_with_logging(test_writer, level="DEBUG", subprocess=True)
