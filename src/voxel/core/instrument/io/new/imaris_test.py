import numpy as np
from pathlib import Path
from typing import Iterator
import time

from voxel.core.utils.geometry.vec import Vec3D
from voxel.core.instrument.io.new.base import WriterMetadata
from voxel.core.instrument.io.new.imaris import ImarisWriter


def generate_test_pattern(width: int, height: int, depth: int) -> np.ndarray:
    """Generate a test volume with easily recognizable patterns.

    Creates diagonal stripes that vary with depth to create an interesting
    3D pattern that's easy to verify in the viewer.
    """
    volume = np.zeros((depth, height, width), dtype=np.uint16)
    max_val = 65535  # Max value for uint16

    # Create diagonal stripes that change with depth
    x, y = np.meshgrid(np.arange(width), np.arange(height))

    for z in range(depth):
        # Vary the stripe frequency with depth
        frequency = 50 + (z / depth) * 100
        pattern = np.sin(x / frequency + y / frequency + z / 20.0)

        # Create binary stripes
        mask = pattern > 0

        # Vary intensity with depth
        intensity = max_val * (0.2 + 0.8 * (z / depth))
        volume[z][mask] = intensity

        # Add some spheres for additional interest
        if z % 32 == 0:  # Every 32 slices
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 4
            sphere_mask = ((x - center_x) ** 2 + (y - center_y) ** 2) < radius**2
            volume[z][sphere_mask] = max_val

    return volume


def generate_batch_iterator(volume: np.ndarray, batch_depth: int) -> Iterator[np.ndarray]:
    """Create an iterator that yields batches from the volume."""
    depth, height, width = volume.shape

    for z in range(0, depth, batch_depth):
        # Handle last batch that might be smaller
        z_end = min(z + batch_depth, depth)
        batch = volume[z:z_end, :height, :width]

        # If last batch is smaller, pad it
        if batch.shape[0] < batch_depth:
            padded_batch = np.zeros((batch_depth, height, width), dtype=volume.dtype)
            padded_batch[: batch.shape[0], :, :] = batch
            batch = padded_batch

        yield batch


def main():
    """Main test function."""
    # Set up output directory in user's home directory
    output_dir = Path.home() / "imaris_test_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_dir}")

    try:
        writer = ImarisWriter(dir=str(output_dir), name="test_writer")

        MULT = 1

        width = writer.chunk_size.x * MULT
        height = writer.chunk_size.y * MULT
        depth = writer.chunk_size.z * MULT

        # Start the writer process
        writer.start()

        # Generate test volume
        print("\nGenerating test pattern...")
        start_time = time.time()
        volume = generate_test_pattern(width, height, depth)
        gen_time = time.time() - start_time
        print(f"Pattern generation took {gen_time:.1f} seconds")

        # Configure the volume
        config = WriterMetadata(
            size=Vec3D(width, height, depth),
            position=Vec3D(0, 0, 0),
            filename="test_pattern",
            channel="patterns",
            timestamp=0,
        )

        print("\nWriting volume...")
        start_time = time.time()

        # Configure and write
        writer.configure(config)
        batch_iterator = generate_batch_iterator(volume, writer.batch_size.z)
        writer.write(batch_iterator)

        write_time = time.time() - start_time

        # Report results
        output_file = output_dir / "test_pattern.ims"
        file_size_mb = output_file.stat().st_size / (1024 * 1024)

        print("\nWrite Complete!")
        print(f"Output file: {output_file}")
        print(f"File size: {file_size_mb:.1f} MB")
        print(f"Write time: {write_time:.1f} seconds")
        print(f"Write speed: {file_size_mb/write_time:.1f} MB/s")

        print("\nPattern Description:")
        print("- Diagonal stripes that vary in frequency with depth")
        print("- Intensity increases from bottom to top")
        print("- Circular patterns appear every 32 slices")
        print("\nYou can now open this file in Imaris to examine the pattern.")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

    finally:
        writer.stop()


if __name__ == "__main__":
    main()
