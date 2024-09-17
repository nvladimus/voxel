import math
from typing import Optional, Dict, List

from voxel.acquisition._config import AcquisitionSpecs
from voxel.acquisition._definitions import TileAcquisitionStrategy
from voxel.acquisition.metadata.base import VoxelMetadata
from voxel.acquisition.model import TilesSet, Tile
from voxel.acquisition.model.scan_plan import ScanPathGenerator, ScanPath
from voxel.acquisition.model.volume import Volume
from voxel.acquisition.persistence import TilePersistenceHandler
from voxel.instrument import VoxelInstrument
from voxel.instrument.channel import VoxelChannel
from voxel.utils.geometry.vec import Vec3D
from voxel.utils.logging import get_logger


class VoxelAcquisition:
    def __init__(self,
                 specs: AcquisitionSpecs,
                 instrument: VoxelInstrument,
                 metadata_handler: VoxelMetadata,
                 scan_path_generator: ScanPathGenerator,
                 tile_persistence_handler: TilePersistenceHandler,
                 name: Optional[str] = None
                 ) -> None:
        self.log = get_logger(f"{self.__class__.__name__}")
        self.name = name
        self.specs = specs
        self.instrument = instrument
        self.metadata = metadata_handler
        self.scan_path_generator = scan_path_generator
        self.tile_persistence = tile_persistence_handler
        self.volume = Volume(
            min_corner=self.instrument.stage.limits_mm[0],
            max_corner=self.instrument.stage.limits_mm[1],
            step_size=self.specs.step_size
        )
        self.volume.add_observer(self._on_volume_change)
        self.tiles: List[TilesSet] = []
        self.generate_tiles()
        self.log.debug(f"Acquisition created with instrument: {instrument}")

    def _on_volume_change(self):
        self.generate_tiles()

    def generate_tiles(self) -> None:
        match self.specs.acquisition_strategy:
            case TileAcquisitionStrategy.MULTI_SHOT:
                tiles_list: List[TilesSet] = []
                for channel_name in self.specs.channels:
                    channel = self.instrument.channels.get(channel_name)
                    channel_tiles = self.generate_tiles_set(channels=[channel])
                    tiles_list.append(channel_tiles)
                self.tiles = tiles_list
            case TileAcquisitionStrategy.ONE_SHOT:
                channels = [self.instrument.channels.get(channel_name) for channel_name in self.specs.channels]
                tiles_list: List[TilesSet] = [self.generate_tiles_set(channels=channels)]
                self.tiles = tiles_list
        self.log.debug(f"Generated {sum(len(tile_set) for tile_set in self.tiles)} tiles")

    @property
    def scan_path(self) -> ScanPath:
        return self.scan_path_generator.generate_path(self.tiles)

    def save_tiles(self) -> None:
        self.tile_persistence.save_tiles(self.tiles, self.scan_path)

    def load_tiles(self) -> None:
        self.tiles, self.scan_path = self.tile_persistence.load_tiles()

    def generate_tiles_set(self, channels: List[VoxelChannel]) -> TilesSet:
        # all channels must have the same fov
        fov = channels[0].fov_um
        for channel in channels:
            if channel.fov_um != fov:
                raise ValueError("Unable to generate tiles with channels of different FOV")
        tiles = {}
        effective_tile_width = fov.x * (1 - self.specs.tile_overlap)
        effective_tile_height = fov.y * (1 - self.specs.tile_overlap)

        x_tiles = math.ceil(self.volume.size.x / effective_tile_width)
        y_tiles = math.ceil(self.volume.size.y / effective_tile_height)

        actual_width = x_tiles * effective_tile_width
        actual_height = y_tiles * effective_tile_height

        tile_count = 0
        for x in range(x_tiles):
            for y in range(y_tiles):
                pos_x = x * effective_tile_width + self.volume.min_corner.x
                pos_y = y * effective_tile_height + self.volume.min_corner.y
                idx = (x, y)
                tile = Tile(
                    idx=idx,
                    tile_number=tile_count,
                    pos=Vec3D(pos_x, pos_y, 0),
                    size=Vec3D(fov.x, fov.y, self.volume.size.z),
                    step_size=self.specs.step_size,
                    channel_names=[channel.name for channel in channels]
                )
                tiles[idx] = tile
                tile_count += 1

        self.volume.max_corner.x = self.volume.min_corner.x + actual_width
        self.volume.max_corner.y = self.volume.min_corner.y + actual_height

        return tiles

    def get_metadata(self) -> Dict:
        return self.metadata.to_dict()
