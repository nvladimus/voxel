import numpy as np
from pathlib import Path

from voxel.core.utils.geometry.vec import Vec3D
from voxel.core.instrument.io.new.base import VoxelWriter, WriterProps
import time


class SimulatedWriter(VoxelWriter):
    """A simulated writer that writes batch data to a text file for testing.

    This writer implements a simple text-based output to verify the multiprocessing
    and batching logic of the VoxelWriter base class.

    :param dir: Output directory path
    :param name: Writer instance name, defaults to "SimulatedWriter"
    """

    def __init__(self, dir: str, name: str = "SimulatedWriter") -> None:
        super().__init__(dir, name)
        self._chunk_size = Vec3D(64, 64, 64)
        self._z_chunks_per_batch = 1

    @property
    def data_type(self) -> np.unsignedinteger:
        """Data type for the written data."""
        return np.uint16

    @property
    def chunk_size(self) -> Vec3D:
        """Size of a single chunk in pixels."""
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value: Vec3D) -> None:
        """Set the chunk size."""
        self._chunk_size = value

    @property
    def z_chunks_per_batch(self) -> int:
        """Number of Z-axis chunks to process in a single batch."""
        return self._z_chunks_per_batch

    @z_chunks_per_batch.setter
    def z_chunks_per_batch(self, value: int) -> None:
        """Set the number of Z-axis chunks per batch."""
        self._z_chunks_per_batch = value

    @property
    def output_file(self) -> Path:
        """Path to the output file."""
        if not self._props:
            raise RuntimeError("Cannot determine output file path without properties")
        return self.dir / f"{self._props.filename}_simulated.txt"

    def _prepare(self) -> None:
        """Prepare the writer by creating the output file."""
        # Create file and write header
        with open(self.output_file, "w") as f:
            f.write("Simulated Volume Write\n")
            f.write(f"Dimensions: {self._props.size}\n")
            f.write(f"Position: {self._props.position}\n")
            f.write(f"Channel: {self._props.channel}\n")
            f.write(f"Timestamp: {self._props.timestamp}\n")
            f.write("-" * 50 + "\n")

    def _process_batch(self, batch_data: np.ndarray) -> None:
        """Process a batch of frames by writing summary statistics to the text file.

        :param batch_data: The batch data to process
        :type batch_data: np.ndarray
        """
        # Calculate some basic statistics
        self.log.info(f"Processing batch with shape {batch_data.shape}")
        self.log.info(f"Batch head: {batch_data[0, 0]}")
        stats = {
            "min": float(np.min(batch_data)),
            "max": float(np.max(batch_data)),
            "mean": float(np.mean(batch_data)),
            "std": float(np.std(batch_data)),
        }

        self.log.info(f"Batch mean: {stats['mean']}")

        # Write batch statistics to file
        with open(self.output_file, "a") as f:
            f.write("\nBatch Statistics:\n")
            f.write(f"Shape: {batch_data.shape}\n")
            for stat_name, value in stats.items():
                f.write(f"{stat_name}: {value}\n")

    def _finalize(self) -> None:
        """Finalize the volume by writing completion message."""
        with open(self.output_file, "a") as f:
            f.write("\nVolume write completed successfully\n")
            f.write("-" * 50 + "\n")


def generate_frames(writer: VoxelWriter, delay: float = 0):
    """Generate test frames with optional delay."""
    batch_count = 0
    size = writer._props.size

    for i in range(size.z):

        if i % writer.batch_shape[0] == 0:
            batch_count += 1
            writer.log.info(f"Batch: {batch_count}")

        frame = np.full((size.y, size.x), batch_count, dtype=writer.data_type)

        if delay:
            time.sleep(delay)  # Simulate slow frame generation
        yield frame


def test_simulated_writer():
    """Test the SimulatedWriter implementation."""

    # Create test directory
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)

    # Create writer instance
    writer = SimulatedWriter(str(test_dir))
    writer.chunk_size = Vec3D(10, 10, 10)

    size = Vec3D(writer.chunk_size.x, writer.chunk_size.y, 100)

    props = WriterProps(
        size=size,
        position=Vec3D(0, 0, 0),
        filename="test_normal",
        channel="test",
        timestamp=0,
    )

    writer.start(props)

    # generator = generate_frames(writer)
    # for frame in generator:
    #     writer.log.info(f"Frame shape: {frame.shape}")
    #     writer.log.info(f"Frame mean: {np.mean(frame)}")

    writer.write(generate_frames(writer, delay=0.05))

    writer.stop()


if __name__ == "__main__":
    from voxel.core.utils.log_config import setup_logging

    setup_logging()
    test_simulated_writer()
