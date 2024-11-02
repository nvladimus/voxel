import tifffile as tf
import numpy as np
from voxel.core.instrument.io.new.base import VoxelWriter, WriterProps
from aicsimageio.vendor import omexml


class TiffVoxelWriter(VoxelWriter):
    """Writer class for voxel data that outputs to a single OME-TIFF file."""

    def __init__(self, *, directory: str, batch_size_px: int = 64, name: str = "TiffVoxelWriter") -> None:
        super().__init__(directory, name)
        self._batch_size_px = batch_size_px
        self.output_file = None
        self.tiff_writer = None

    @property
    def data_type(self) -> np.dtype:
        return np.uint16

    @property
    def batch_size_px(self) -> int:
        return self._batch_size_px

    @batch_size_px.setter
    def batch_size_px(self, value: int) -> None:
        self._batch_size_px = value

    def configure(self, props: WriterProps) -> None:
        super().configure(props)
        self.output_file = self.dir / f"{self._props.file_name}.ome.tiff"
        num_frames = f"Configured OME-TIFF writer with {self._props.frame_count} frames"
        frame_shape = f"of shape {self._props.frame_shape.x}px x {self._props.frame_shape.y}px"
        batch_size = f"in batches of {self._batch_size_px}."
        self.log.info(f"{num_frames} {frame_shape} {batch_size}")

    def _initialize(self) -> None:
        if self.output_file.exists():
            self.output_file.unlink()
        self.tiff_writer = tf.TiffWriter(self.output_file, bigtiff=True, ome=True)
        self.pages_written = 0

        # Prepare OME metadata
        self.ome_metadata = tf.ome_metadata(
            axes="ZYX",
            shape=(self._props.frame_count, self._props.frame_shape.y, self._props.frame_shape.x),
            dtype=self.data_type,
        )

    def _process_batch(self, batch_data: np.ndarray, batch_count: int) -> None:
        self.tiff_writer.write(
            batch_data,
            metadata=None,  # OME metadata is added at the end
            photometric="minisblack",
            contiguous=False,
        )
        self.pages_written += batch_data.shape[0]
        self.log.info(f"Batch {batch_count} written to {self.output_file}")

    def _finalize(self) -> None:
        try:
            # Update the OME-XML metadata with the actual number of pages written
            self.tiff_writer.write(
                [],  # Empty data
                metadata=self.ome_metadata,
                photometric="minisblack",
                contiguous=False,
            )
            self.tiff_writer.close()
        except Exception as e:
            self.log.error(f"Failed to close TiffWriter: {e}")
        self.log.info(
            f"Processed {self._frame_count} frames in {self._batch_count} batches and saved to {self.output_file}."
        )


def generate_checkered_frames(frame_count, frame_shape, data_type):
    """Generate test frames with checkerboard patterns."""
    tile_size = 32  # Size of the checkerboard tiles
    for frame_z in range(frame_count):
        # Create a checkerboard pattern
        num_tiles_x = frame_shape.x // tile_size
        num_tiles_y = frame_shape.y // tile_size
        checkerboard = np.indices((num_tiles_y, num_tiles_x)).sum(axis=0) % 2
        checkerboard = np.kron(checkerboard, np.ones((tile_size, tile_size)))

        # Adjust pattern over time
        pattern_shift = frame_z % tile_size
        frame = np.roll(checkerboard, shift=pattern_shift, axis=1)

        # Scale to full intensity range
        frame = (frame * 255).astype(data_type)

        yield frame


def test_tiffwriter():
    """Test the OME-TIFF voxel writer with realistic image data."""
    from voxel.core.utils.geometry.vec import Vec2D, Vec3D
    import tifffile

    def verify_output(tiff_file_path) -> None:
        # Load the voxel data
        with tifffile.TiffFile(tiff_file_path) as tif:
            num_pages = len(tif.pages)
            if num_pages == 0:
                print(f"<tifffile.TiffFile '{tiff_file_path.name}'> contains no pages")
                return
            shape = tif.series[0].shape
            print(f"Voxel data shape: {shape}")

        # Verify the number of frames
        expected_frames = NUM_BATCHES * writer.batch_size_px
        if shape[0] != expected_frames:
            print(f"Error: Expected {expected_frames} frames, but found {shape[0]}")
        else:
            print("All frames successfully written.")

    def display_output(tiff_file_path, num_frames) -> None:
        from matplotlib import pyplot as plt

        with tifffile.TiffFile(tiff_file_path) as tif:
            num_frames = len(tif.pages)
            print(f"The TIFF file contains {num_frames} frames.")

            # Iterate over frames
            for i, page in enumerate(tif.pages):
                image = page.asarray()

                # Display the frame
                plt.imshow(image, cmap="gray")
                plt.title(f"Frame {i+1}")
                plt.colorbar()
                plt.show()

                if i >= num_frames - 1:
                    break

    writer = TiffVoxelWriter(directory="test_output", name="tiff_writer")

    NUM_BATCHES = 10
    frame_shape = Vec2D(512, 512)
    frame_count = writer.batch_size_px * NUM_BATCHES
    props = WriterProps(
        frame_count=frame_count,
        frame_shape=frame_shape,
        position=Vec3D(0, 0, 0),
        file_name="voxel_data",
    )

    writer.configure(props)
    writer.log.info(f"Expecting: {frame_count} frames of {frame_shape.x}x{frame_shape.y} in {NUM_BATCHES} batch(es)")
    writer.start()

    try:
        for frame in generate_checkered_frames(frame_count, frame_shape, writer.data_type):
            writer.add_frame(frame)
    except Exception as e:
        writer.log.error(f"Test failed: {e}")
    finally:
        writer.stop()

    verify_output(writer.output_file)
    display_output(writer.output_file, 1)


if __name__ == "__main__":
    from voxel.core.utils.logging import run_with_logging

    run_with_logging(test_tiffwriter, level="DEBUG", subprocess=True)
