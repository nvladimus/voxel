import json
import math
import pickle
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, List

import numpy as np

from instrument import VoxelChannel
from utils.logging import get_logger
from voxel.acquisition.scan_plan import ScanPlanStrategy, ParametricScanPlan, Coordinate
from voxel.instrument.devices.laser.cobolt.skyra import StrEnum
from voxel.utils.geometry.cuboid import Cuboid
from voxel.utils.geometry.vec import Vec3D, Vec2D, Plane


class TileNeighbour(StrEnum):
    LEFT = 'left'
    RIGHT = 'right'
    UP = 'up'
    DOWN = 'down'


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

DEFAULT_TILE_OVERLAP = 0.15


@dataclass
class FrameStack:
    idx: Coordinate
    pos: Vec3D
    size: Vec3D
    step_size: float
    file_name_prefix: str
    tile_number: int = 0
    settings: Optional[Dict[str, Dict[str, Any]]] = None

    @property
    def num_frames(self):
        return math.ceil(self.size.z / self.step_size)

    def get_size_mb(self, channel: 'VoxelChannel') -> float:
        frame_size_mb = channel.camera.frame_size_px.x * channel.camera.frame_size_px.y * np.dtype(
            channel.writer.data_type).itemsize / 1024 ** 2
        return frame_size_mb * self.num_frames

    def get_file_name(self, channel: 'VoxelChannel') -> str:
        return f'{self.file_name_prefix}_{self.tile_number:06}_ch_{channel.name}'

    def __str__(self):
        return f"Tile {self.tile_number} at {self.pos} with size {self.size}"

    def __repr__(self):
        return f"Tile {self.tile_number} at {self.pos} with size {self.size}"


class VoxelVolumeError(Exception):
    pass


class Volume(Cuboid):
    def __init__(self,
                 step_size: float,
                 stage_limits_mm: Tuple[Vec3D, Vec3D],
                 tile_overlap: float,
                 tile_name_prefix: str,
                 scan_strategy: ScanPlanStrategy = ParametricScanPlan()) -> None:
        self.tile_name_prefix = tile_name_prefix
        self.scan_strategy = scan_strategy
        self.scan_path = []
        self.tile_overlap = tile_overlap if 0 <= tile_overlap < 1 else DEFAULT_TILE_OVERLAP
        self._step_size = step_size
        self.log = get_logger(self.__class__.__name__)
        super().__init__(stage_limits_mm[0], stage_limits_mm[1])

    def generate_tiles(self, fov: Vec2D) -> Tuple[Dict[Coordinate, FrameStack], List[Tuple[int, int]]]:
        tiles = {}
        effective_tile_width = fov.x * (1 - self.tile_overlap)
        effective_tile_height = fov.y * (1 - self.tile_overlap)

        x_tiles = int(self.size.x // effective_tile_width)
        y_tiles = int(self.size.y // effective_tile_height)

        actual_width = x_tiles * effective_tile_width
        actual_height = y_tiles * effective_tile_height

        tile_count = 0
        for x in range(x_tiles):
            for y in range(y_tiles):
                pos_x = x * effective_tile_width + self.min_corner.x
                pos_y = y * effective_tile_height + self.min_corner.y
                idx = (x, y, 0)
                tile = FrameStack(
                    idx=idx,
                    tile_number=tile_count,
                    pos=Vec3D(pos_x, pos_y, 0),
                    size=Vec3D(fov.x, fov.y, self.size.z),
                    step_size=self.step_size,
                    file_name_prefix=self.tile_name_prefix
                )
                tiles[idx] = tile
                tile_count += 1

        self.max_corner.x = self.min_corner.x + actual_width
        self.max_corner.y = self.min_corner.y + actual_height

        return tiles, self.scan_strategy.generate_plan(tiles)

    @property
    def step_size(self):
        return self._step_size

    @step_size.setter
    def step_size(self, step_size: int):
        self._step_size = step_size
        self.size.z = math.ceil(self.size.z / step_size) * step_size

    @property
    def min_z(self):
        return self.min_corner.z

    @min_z.setter
    def min_z(self, plane: Plane):
        min_z = plane.min_corner.z
        super().min_z = min_z
        valid_min_z = self.max_corner.z - (math.ceil((self.max_corner.z - min_z) / self.step_size) * self.step_size)
        self.min_corner.z = valid_min_z

    @property
    def max_z(self):
        return self.max_corner.z

    @max_z.setter
    def max_z(self, plane: Plane):
        max_z = plane.max_corner.z
        super().max_z = max_z
        valid_max_z = (math.ceil((max_z - self.min_z) / self.step_size) * self.step_size) + self.min_z
        self.max_corner.z = valid_max_z


class TilePersistenceStrategy(ABC):
    @abstractmethod
    def save_tiles(self, tiles: Dict[Coordinate, FrameStack], file_path: str) -> None:
        pass

    @abstractmethod
    def load_tiles(self, file_path: str) -> Dict[Coordinate, FrameStack]:
        pass


class JsonifyTiles(TilePersistenceStrategy):
    def save_tiles(self, tiles: Dict[Coordinate, FrameStack], file_path: str) -> None:
        with open(file_path, 'w') as f:
            json.dump({str(k): v.__dict__ for k, v in tiles.items()}, f, indent=2)

    def load_tiles(self, file_path: str) -> Dict[Coordinate, FrameStack]:
        with open(file_path) as f:
            data = json.load(f)
        return {eval(k): FrameStack(**v) for k, v in data.items()}


class PickleTiles(TilePersistenceStrategy):
    def save_tiles(self, tiles: Dict[Coordinate, FrameStack], file_path: str) -> None:
        with open(file_path, 'wb') as f:
            pickle.dump(tiles, f)

    def load_tiles(self, file_path: str) -> Dict[Coordinate, FrameStack]:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
