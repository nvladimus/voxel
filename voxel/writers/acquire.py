import logging

COMPRESSION_TYPES = {
    "None":  "Zarr",
    "LZ4Shuffle":  "ZarrBlosc1ZstdByteShuffle",
    "ZSTDShuffle": "ZarrBlosc1Lz4ByteShuffle",
}

class StackWriter:
    """Class for writing a stack of frames to a file on disk."""

    def __init__(self, runtime: acquire.Runtime(),
                 image_rows: int, image_columns: int, image_count: int,
                 first_img_centroid_x: float, first_img_centroid_y: float,
                 pixel_x_size_um: float, pixel_y_size_um: float,
                 pixel_z_size_um: float,
                 chunk_dimension_order: tuple, compression_style: str,
                 data_type: str, dest_path: Path, stack_name: str,
                 channel_name: str, viz_color_hex: str):

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # Lookups for deducing order.
        self.dim_map = {'x': 0, 'y': 1, 'z': 2, 'c': 3, 't': 4}
        # metadata to create the file.
        self.cols = image_columns
        self.rows = image_rows
        self.img_count = image_count
        self.first_img_centroid_x_um = first_img_centroid_x
        self.first_img_centroid_y_um = first_img_centroid_y
        self.pixel_x_size_um = pixel_x_size_um
        self.pixel_y_size_um = pixel_y_size_um
        self.pixel_z_size_um = pixel_z_size_um
        self.channel_name = channel_name
        self.chunk_dim_order = chunk_dimension_order
        self.dest_path = dest_path
        self.stack_name = stack_name \
            if stack_name.endswith(".zarr") else f"{stack_name}.zarr"
        self.hex_color = viz_color_hex

        # instantiate acquire runtime
        self.runtime = runtime
        # instantiate acquire device manager
        self.dm = self.runtime.device_manager()
        # instantiate acquire runtime configuration
        self.p = self.runtime.get_configuration()
        # set compression type
        compression_style = writer_cfg['compression']
        valid = list(COMPRESSION_TYPES.keys())
        if compression_style not in valid:
            raise ValueError("compression type must be one of %r." % valid)
        self.p.video[0].storage.identifier = self.dm.select(acquire.DeviceKind.Storage, COMPRESSION_TYPES[compression_style])
        # set file name and path
        filepath = str((self.dest_path/Path(f"{self.stack_name}")).absolute())
        self.p.video[0].storage.settings.filename = filepath
        # update acquire runtime
        self.p = self.runtime.set_configuration(self.p)

    def start(self):
        self.log.info('File writer start passes for acquire')
        pass

    def close(self):
        self.log.info('File writer stop passes for acquire')
        pass