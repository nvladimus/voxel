import numpy as np
from datetime import datetime
from pathlib import Path
from voxel.core.utils.geometry.vec import Vec3D
from voxel.core.instrument.io.new.base import VoxelWriter, WriterState
from PyImarisWriter import PyImarisWriter as pw

CHUNK_SIZE = Vec3D(x=64, y=64, z=64)


class ImarisProgressCallback(pw.CallbackClass):
    """Adapter to map VoxelWriter progress to ImarisWriter progress callback."""

    def __init__(self, writer: "ImarisWriter"):
        self.writer = writer

    def RecordProgress(self, progress: float, total_bytes_written: int):
        """Called by ImarisWriter SDK to report progress."""
        self.writer.progress = progress


class ImarisWriter(VoxelWriter):
    """Writer implementation for Imaris files (.ims format).

    This writer efficiently handles large volumetric datasets by processing them
    in chunks using the ImarisWriter SDK.
    """

    def __init__(self, dir: str, name: str) -> None:
        """Initialize the Imaris writer.

        :param dir: Output directory path
        :param name: Writer instance name
        """
        super().__init__(dir, name)

        self.progress = 0.0

        # ImarisWriter specific members
        self._converter: pw.ImageConverter | None = None
        self._current_block = pw.ImageSize(x=0, y=0, z=0, c=0, t=0)

    @property
    def data_type(self) -> np.unsignedinteger:
        """Data type for the written data."""
        return np.dtype(np.uint16)

    @property
    def chunk_size(self) -> Vec3D:
        """Size of a single chunk in pixels."""
        return CHUNK_SIZE

    @property
    def z_chunks_per_batch(self) -> int:
        """Number of Z chunks to process in each batch."""
        return 1

    def _prepare(self) -> None:
        # Create Imaris image converter
        options = pw.Options()
        options.mNumberOfThreads = 8
        options.mForceFileBlockSizeZ = True

        # Initialize image sizes
        image_size = pw.ImageSize(
            x=self.metadata.width,
            y=self.metadata.height,
            z=self.metadata.depth,
            c=1,  # Single channel for now
            t=1,  # Single timepoint for now
        )

        sample_size = pw.ImageSize(x=1, y=1, z=1, c=1, t=1)

        block_size = pw.ImageSize(x=self.chunk_size.x, y=self.chunk_size.y, z=self.chunk_size.z, c=1, t=1)

        # Define dimension sequence (order in which dimensions are written)
        dimension_sequence = pw.DimensionSequence("z", "y", "x", "c", "t")

        # Create the converter
        output_path = str(Path(self.dir) / f"{self.metadata.filename}.ims")

        self._converter = pw.ImageConverter(
            datatype=np.dtype(self.data_type).name,
            image_size=image_size,
            sample_size=sample_size,
            dimension_sequence=dimension_sequence,
            block_size=block_size,
            output_filename=output_path,
            options=options,
            application_name="VoxelWriter",
            application_version="1.0",
            progress_callback_class=ImarisProgressCallback(self),
        )
        self.log.info(f"Imaris writer prepared for {output_path}")

    def _process_current_batch(self) -> None:
        """Process the current batch from shared memory."""
        if not self._converter:
            raise RuntimeError("ImarisWriter not configured")

        try:
            self.log.info("Getting data from shared memory")
            shared_array = np.ndarray(self.batch_shape, dtype=self.data_type, buffer=self._buffer.read_buf)

            # Process each Z chunk in the batch
            z_chunks = shared_array.shape[0] // self.chunk_size.z
            self.log.info(f"Processing {z_chunks} Z chunks")

            for z_chunk in range(z_chunks):
                z_start = z_chunk * self.chunk_size.z
                z_end = z_start + self.chunk_size.z

                chunk_data = shared_array[z_start:z_end, :, :]

                self.log.info(f"Writing chunk {z_chunk + 1}/{z_chunks}")
                if self._converter.NeedCopyBlock(self._current_block):
                    self._converter.CopyBlock(chunk_data, self._current_block)

                self._current_block.z += 1

            self.log.info("Batch processing completed successfully")

        except Exception as e:
            self.log.error(f"Error processing batch: {str(e)}")
            self.state = WriterState.ERROR
            raise

    def _finalize(self) -> None:
        """Finalize the Imaris file writing process."""
        if not self._converter:
            raise RuntimeError("ImarisWriter not configured")

        try:
            # Set up image extents (using dummy values for now)
            extents = pw.ImageExtents(0, 0, 0, 1, 1, 1)

            # Set up pw.parameters
            params = pw.Parameters()

            # Set up time infos (single timepoint for now)
            time_infos: list[datetime] = [datetime.now()]

            # Set up pw.color info (default red for now)
            color_info = pw.ColorInfo()
            color_info.set_base_color(pw.Color(1, 0, 0, 1))
            color_infos = [color_info]

            # Finalize the file
            self._converter.Finish(
                image_extents=extents,
                parameters=params,
                time_infos=time_infos,
                color_infos=color_infos,
                adjust_color_range=True,
            )

            # Cleanup
            self._converter.Destroy()
            self._converter = None

        except Exception as e:
            self.state = WriterState.ERROR
            raise RuntimeError(f"Failed to finalize Imaris file: {str(e)}") from e

    def _subprocess_cleanup(self) -> None:
        if self._converter:
            try:
                self._converter.Destroy()
            except Exception as e:
                self.log.error(f"Error during converter destruction: {str(e)}")
                pass
            self._converter = None
