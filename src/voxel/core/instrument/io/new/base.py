from dataclasses import dataclass
from multiprocessing import Event, Value
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path
from time import sleep
import numpy as np

from voxel.core.instrument.io.data_structures.shared_double_buffer import SharedDoubleBuffer
from voxel.core.utils.geometry.vec import Vec3D
from voxel.core.utils.logging import LoggingSubprocess


@dataclass
class WriterProps:
    """Configuration properties for a frame stack writer."""

    size: Vec3D
    position: Vec3D
    file_name: str

    def pad(self, chunk_size: Vec3D, z_chunks_per_batch: int) -> None:
        """Pad the dimensions to match the batch size."""
        z_size = chunk_size.z * z_chunks_per_batch
        self.size.x = (self.size.x + chunk_size.x - 1) // chunk_size.x * chunk_size.x
        self.size.y = (self.size.y + chunk_size.y - 1) // chunk_size.y * chunk_size.y
        self.size.z = (self.size.z + z_size - 1) // z_size * z_size


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

        self.chunk_size = Vec3D(64, 64, 64)
        self.z_chunks_per_batch = 1
        self.data_type = np.dtype(np.uint16)

        self.props = None
        self.dbl_buf = None
        self.subproc_mem = None
        self.subproc_mem_name = None

        self.subproc_mem_idx = Value("i", 1)

        # Events for synchronization
        self.needs_processing = Event()
        self.running_flag = Event()

        self.frame_count = 0
        self.batch_count = 0
        self.timeout = 5

    @property
    def batch_size_z(self) -> int:
        """The number of z-chunks per batch

        :return: Size of batch in Z dimension
        :rtype: int
        """
        return self.z_chunks_per_batch * self.chunk_size.z

    def start(self, props: WriterProps) -> None:
        """Start the writer with the given configuration

        :param props: Configuration properties
        :type props: WriterProps
        :raises RuntimeError: If writer fails to start
        """
        try:
            self.props = props
            self.props.pad(self.chunk_size, self.z_chunks_per_batch)

            batch_shape = (self.batch_size_z, self.props.size.y, self.props.size.x)
            self.dbl_buf = SharedDoubleBuffer(batch_shape, self.data_type.str)

            self.running_flag.set()
            self.needs_processing.clear()
            self.log.debug(f"Started writer with size: {self.props.size}")
            super().start()
        except Exception as e:
            if self.dbl_buf:
                self.dbl_buf.close_and_unlink()
            raise RuntimeError(f"Failed to start writer: {e}")

    def stop(self) -> None:
        """Stop the writer and clean up resources"""

        while self.needs_processing.is_set():
            sleep(0.001)

        self._switch_buffers()

        # Wait for final processing to complete
        while self.needs_processing.is_set():
            sleep(0.001)

        self.log.debug("Stopping writer")
        self.running_flag.clear()
        self.join()

        if self.dbl_buf:
            self.dbl_buf.close_and_unlink()
            self.dbl_buf = None
        self.log.debug("Writer stopped")

    def _run(self) -> None:
        """Main writer loop"""

        self.subproc_mem_blocks = [
            SharedMemory(self.dbl_buf.mem_blocks[0].name),
            SharedMemory(self.dbl_buf.mem_blocks[1].name),
        ]

        batch_count = 1
        while self.running_flag.is_set():
            if self.needs_processing.is_set():
                try:
                    self.log.info(f"Processing batch {batch_count} in memory block {self.subproc_mem_idx.value}")
                    mem_block = self.subproc_mem_blocks[self.subproc_mem_idx.value]
                    batch_data = np.ndarray(self.dbl_buf.shape, dtype=self.data_type, buffer=mem_block.buf)
                    self._process_batch(batch_data, batch_count)
                except Exception as e:
                    self.log.error(f"Error processing batch: {e}")
                finally:
                    self.needs_processing.clear()
                    batch_count += 1
            sleep(0.1)

    def add_frame(self, frame: np.ndarray) -> None:
        """Add a frame to the writer

        :param frame: Frame data to add
        :type frame: np.ndarray
        """
        buffer_full = self.frame_count > 0 and self.frame_count % self.batch_size_z == 0

        if buffer_full:
            self._switch_buffers()

        self.dbl_buf.add_frame(frame)
        self.frame_count += 1

    def _switch_buffers(self) -> None:
        """Switch read and write buffers with proper synchronization"""
        # Wait for any ongoing processing to complete
        while self.needs_processing.is_set():
            sleep(0.001)

        # Toggle buffers
        self.dbl_buf.toggle_buffers()
        self.subproc_mem_idx.value = 1 if self.subproc_mem_idx.value == 0 else 0

        # Signal that new data needs processing
        self.needs_processing.set()

        # Wait for processing to start before continuing
        while not self.needs_processing.is_set():
            sleep(0.001)

        self.batch_count += 1

    def _process_batch(self, batch_data: np.ndarray, batch_count: int) -> None:
        """Process a batch of data with validation and metrics

        :param batch_data: The batch of frame data to process
        :type batch_data: np.ndarray
        :param batch_count: Current batch number (1-based)
        :type batch_count: int
        """
        num_frames = batch_data.shape[0]
        start_frame = (batch_count - 1) * self.batch_size_z
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
            f"Frames: {stats['frames_processed']:3d} ({stats['frame_range']}) | "
            f"Values: min={stats['min_value']:3d}, max={stats['max_value']:3d}, "
            f"mean={stats['mean_value']:.1f} | "
            f"Errors: {stats['validation_errors']}"
        )

        if frame_errors:
            self.log.debug("Validation errors:\n" + "\n".join(frame_errors))


def generate_frames(writer: VoxelWriter):
    """Generate test frames with sequential values

    :param writer: VoxelWriter instance to generate frames for
    :type writer: VoxelWriter
    :return: Generator yielding test frames
    :rtype: Generator[np.ndarray, None, None]
    """
    size = writer.props.size
    batch_idx = 0

    for frame_z in range(size.z):
        # Fill frame with the current frame index
        frame = np.full((size.y, size.x), frame_z, dtype=writer.data_type)

        # Log frame generation for debugging
        if frame_z % writer.batch_size_z == 0:
            batch_idx += 1

        yield frame


def test_writer():
    """Test the writer with power of 2 dimensions"""
    writer = VoxelWriter("test", "test_writer")

    # Configure for 64-frame batches
    NUM_BATCHES = 4
    writer.z_chunks_per_batch = 1
    writer.chunk_size = Vec3D(64, 64, 64)
    size = Vec3D(128, 128, 64 * NUM_BATCHES)

    writer.log.info("\nRunning power of 2 test")
    writer.log.info(f"Input dimensions: {size}")

    writer.log.info(f"Expected batches: {NUM_BATCHES}")

    props = WriterProps(size, Vec3D(0, 0, 0), "test_file_power_of_2")
    writer.start(props)

    try:
        for frame in generate_frames(writer):
            writer.add_frame(frame)

    except Exception as e:
        writer.log.error(f"Test failed: {e}")
    finally:
        writer.stop()


if __name__ == "__main__":
    from voxel.core.utils.logging import initialize_subprocess_listener, setup_logging

    setup_logging(level="DEBUG")
    listener = initialize_subprocess_listener()

    try:
        test_writer()
    finally:
        listener.stop()
