import tifffile as tf
import numpy as np
from voxel.core.instrument.io.new.base import VoxelWriter, WriterMetadata, WriterDType
import xml.etree.ElementTree as ET


class TiffVoxelWriter(VoxelWriter):
    """Writer class for voxel data that outputs to a single OME-TIFF file."""

    def __init__(self, *, directory: str, batch_size_px: int = 64, name: str = "TiffVoxelWriter") -> None:
        super().__init__(directory, name)
        self._batch_size_px = batch_size_px
        self.output_file = None
        self.tiff_writer = None
        self.ome_xml = None
        self.pages_written = 0
        self.axes_order = "ZYX"  # Adjusted axes order based on your data shape

    @property
    def data_type(self) -> WriterDType:
        return "uint16"

    @property
    def batch_size_px(self) -> int:
        return self._batch_size_px

    @batch_size_px.setter
    def batch_size_px(self, value: int) -> None:
        self._batch_size_px = value

    def configure(self, metadata: WriterMetadata) -> None:
        super().configure(metadata)
        self.metadata.pixel_type = self.data_type
        self.output_file = self.dir / f"{self.metadata.file_name}.ome.tiff"
        num_frames = f"Configured OME-TIFF writer with {self.metadata.frame_count} frames"
        frame_shape = f"of shape {self.metadata.frame_shape.x}px x {self.metadata.frame_shape.y}px"
        batch_size = f"in batches of {self._batch_size_px}."
        self.log.info(f"{num_frames} {frame_shape} {batch_size}")

    def _initialize(self) -> None:
        if self.output_file.exists():
            self.output_file.unlink()
        self.tiff_writer = tf.TiffWriter(self.output_file, bigtiff=True, ome=True)
        self.pages_written = 0

        self.ome_xml = self._generate_ome_xml()

    def _process_batch(self, batch_data: np.ndarray, batch_count: int) -> None:
        # For the first batch, include the OME-XML metadata
        if batch_count == 1:
            metadata = {"axes": self.axes_order, "ome_xml": self.ome_xml}
        else:
            metadata = {"axes": self.axes_order}

        self.tiff_writer.write(
            batch_data,
            photometric="minisblack",
            metadata=metadata,
            contiguous=True,
        )
        self.pages_written += batch_data.shape[0]
        self.log.info(f"Batch {batch_count} written to {self.output_file}")

    def _finalize(self) -> None:
        try:
            self.tiff_writer.close()
        except Exception as e:
            self.log.error(f"Failed to close TiffWriter: {e}")
        self.log.info(
            f"Processed {self.metadata.frame_count} frames in {self._batch_count} batches. Saved to {self.output_file}."
        )

    def _generate_ome_xml(self) -> str:
        """Generate OME-XML metadata for the image stack."""
        OME_NS = "http://www.openmicroscopy.org/Schemas/OME/2016-06"
        xsi_NS = "http://www.w3.org/2001/XMLSchema-instance"
        schema_location = "http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd"

        # Register namespaces
        ET.register_namespace("", OME_NS)
        ET.register_namespace("xsi", xsi_NS)

        # Create root element
        root = ET.Element(
            "{%s}OME" % OME_NS,
            attrib={
                "{%s}schemaLocation" % xsi_NS: schema_location,
            },
        )

        # Create Image element
        image = ET.SubElement(root, "Image", attrib={"ID": "Image:0", "Name": self.metadata.file_name})

        # Create Pixels element
        pixels_attrib = {
            "ID": "Pixels:0",
            "DimensionOrder": "XYZCT",
            "Type": self.metadata.pixel_type,
            "SizeX": str(self.metadata.frame_shape.x),
            "SizeY": str(self.metadata.frame_shape.y),
            "SizeZ": str(self.metadata.frame_count),
            "SizeC": str(len(self.metadata.channel_names)),
            "SizeT": "1",
        }

        # Physical sizes
        pixels_attrib.update(
            {
                "PhysicalSizeX": str(self.metadata.voxel_size.x),
                "PhysicalSizeXUnit": self.metadata.voxel_size_unit,
                "PhysicalSizeY": str(self.metadata.voxel_size.y),
                "PhysicalSizeYUnit": self.metadata.voxel_size_unit,
                "PhysicalSizeZ": str(self.metadata.voxel_size.z),
                "PhysicalSizeZUnit": self.metadata.voxel_size_unit,
            }
        )

        pixels = ET.SubElement(image, "Pixels", attrib=pixels_attrib)

        # Create Channel elements
        num_channels = int(pixels_attrib["SizeC"])
        channel_names = self.metadata.channel_names or [f"Channel{i}" for i in range(num_channels)]
        for c in range(num_channels):
            _ = ET.SubElement(
                pixels,
                "Channel",
                attrib={
                    "ID": f"Channel:0:{c}",
                    "Name": channel_names[c],
                    "SamplesPerPixel": "1",
                },
            )

        # Convert XML tree to string
        ome_xml = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
        return ome_xml


def test_tiffwriter():
    """Test the OME-TIFF voxel writer with realistic image data."""
    from voxel.core.utils.geometry.vec import Vec2D, Vec3D
    from voxel.core.instrument.io.new.base import generate_spiral_frames

    writer = TiffVoxelWriter(directory="test_output", name="tiff_writer")

    NUM_BATCHES = 10
    frame_shape = Vec2D(512, 512)
    frame_count = writer.batch_size_px * NUM_BATCHES
    metadata = WriterMetadata(
        frame_count=frame_count,
        frame_shape=frame_shape,
        position=Vec3D(0, 0, 0),
        file_name="voxel_data",
        voxel_size=Vec3D(0.1, 0.1, 1.0),  # Example voxel sizes in micrometers
        voxel_size_unit="µm",
        channel_names=["Channel0"],
        # pixel_type is set automatically based on data_type
    )

    writer.configure(metadata)
    writer.log.info(f"Expecting: {frame_count} frames of {frame_shape.x}x{frame_shape.y} in {NUM_BATCHES} batches")
    writer.start()

    try:
        for frame in generate_spiral_frames(frame_count, frame_shape, writer.data_type):
            writer.add_frame(frame)
    except Exception as e:
        writer.log.error(f"Test failed: {e}")
    finally:
        writer.stop()

    # Verify the OME metadata
    with tf.TiffFile(writer.output_file) as tif:
        ome_metadata = tif.ome_metadata
        print("OME Metadata:")
        print(ome_metadata)


if __name__ == "__main__":
    from voxel.core.utils.logging import run_with_logging

    run_with_logging(test_tiffwriter, level="DEBUG", subprocess=True)
