import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional, Dict, Any, TypedDict, List

import numpy as np

from voxel.acquisition.model import ParametricScanPlan
from voxel.acquisition.model.scan_plan import ScanPlanStrategy, Coordinate
from voxel.instrument.channel import VoxelChannel
from voxel.utils.geometry.vec import Vec3D
from voxel.utils.logging import get_logger


# example of tile settings
# {
#     "red": {
#         VoxelDeviceType.CAMERA: {
#             "exposure_time": 20,
#             "binning": 1,
#         },
#         VoxelDeviceType.Laser: {
#             "power_mw": 50,
#         }
#     },
#     "green": { ... },
#     "blue": { ... },
# }


@dataclass
class Tile:
    idx: Coordinate
    pos: Vec3D
    size: Vec3D
    step_size: float
    file_name_prefix: str
    tile_number: int
    channel_names: List[str]
    channels: Optional[Dict[str, VoxelChannel]] = None
    settings: Optional[Dict[str, Dict[str, Any]]] = None

    def __post_init__(self):
        self.log = get_logger(self.__class__.__name__)

    @property
    def num_frames(self):
        return math.ceil(self.size.z / self.step_size)

    def get_size_mb(self, channel: 'VoxelChannel') -> float:
        frame_size_mb = channel.camera.frame_size_px.x * channel.camera.frame_size_px.y * np.dtype(
            channel.writer.data_type).itemsize / 1024 ** 2
        return frame_size_mb * self.num_frames

    def get_total_size_mb(self) -> float:
        return sum(self.get_size_mb(channel) for channel in self.channels.values())

    def get_file_name(self, channel: 'VoxelChannel') -> str:
        return f'{self.file_name_prefix}_{self.tile_number:06}_ch_{channel.name}'

    def __str__(self):
        return f"Tile {self.tile_number} at {self.pos} with size {self.size}"

    def __repr__(self):
        return f"Tile {self.tile_number} at {self.pos} with size {self.size}"


Tiles = TypedDict[Coordinate, Tile]


class TileNeighbour(StrEnum):
    LEFT = 'left'
    RIGHT = 'right'
    UP = 'up'
    DOWN = 'down'


class TilePlan:
    def __init__(self, tiles: Tiles, scan_strategy: ScanPlanStrategy = ParametricScanPlan()) -> None:
        self.log = get_logger(self.__class__.__name__)
        self.tiles: Tiles = tiles
        self._scan_strategy: ScanPlanStrategy = scan_strategy
        self._scan_path: Optional[List[Coordinate]] = None

    @property
    def scan_path(self):
        if self._scan_path is None:
            self._scan_path = self.scan_strategy.generate_plan(self.tiles)
        return self._scan_path

    @property
    def scan_strategy(self):
        return self._scan_strategy

    @scan_strategy.setter
    def scan_strategy(self, scan_strategy: ScanPlanStrategy):
        self._scan_strategy = scan_strategy
        self._scan_path = None

    def get_neighbour(self, tile: Tile, direction: TileNeighbour) -> Optional[Tile]:
        x, y = tile.idx
        if direction == TileNeighbour.LEFT:
            x -= 1
        elif direction == TileNeighbour.RIGHT:
            x += 1
        elif direction == TileNeighbour.UP:
            y += 1
        elif direction == TileNeighbour.DOWN:
            y -= 1
        return self.tiles.get((x, y), None)
