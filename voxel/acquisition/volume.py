import json
import math
import pickle
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Dict, Tuple, Any, Optional

from utils.logging import get_logger
from voxel.acquisition.scan_plan import ScanPlanStrategy, ParametricScanPlan, Coordinate
from voxel.instrument.devices.laser.cobolt.skyra import StrEnum
from voxel.instrument.devices.linear_axis import VoxelLinearAxis
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
class Tile:
    idx: Coordinate
    pos: Vec3D
    size: Vec3D
    step_size: float
    file_name_prefix: str
    tile_number: int = 0
    current_channel: str = "only"
    settings: Optional[Dict[str, Dict[str, Any]]] = None

    @property
    def file_name(self) -> str:
        return f'{self.file_name_prefix}_{self.tile_number:06}_ch_{self.current_channel}'

    def __str__(self):
        return f"Tile {self.tile_number} at {self.pos} with size {self.size}"

    def __repr__(self):
        return f"Tile {self.tile_number} at {self.pos} with size {self.size}"


class TilePersistenceStrategy(ABC):
    @abstractmethod
    def save_tiles(self, tiles: Dict[Coordinate, Tile], file_path: str) -> None:
        pass

    @abstractmethod
    def load_tiles(self, file_path: str) -> Dict[Coordinate, Tile]:
        pass


class JsonifyTiles(TilePersistenceStrategy):
    def save_tiles(self, tiles: Dict[Coordinate, Tile], file_path: str) -> None:
        with open(file_path, 'w') as f:
            json.dump({str(k): v.__dict__ for k, v in tiles.items()}, f, indent=2)

    def load_tiles(self, file_path: str) -> Dict[Coordinate, Tile]:
        with open(file_path) as f:
            data = json.load(f)
        return {eval(k): Tile(**v) for k, v in data.items()}


class PickleTiles(TilePersistenceStrategy):
    def save_tiles(self, tiles: Dict[Coordinate, Tile], file_path: str) -> None:
        with open(file_path, 'wb') as f:
            pickle.dump(tiles, f)

    def load_tiles(self, file_path: str) -> Dict[Coordinate, Tile]:
        with open(file_path, 'rb') as f:
            return pickle.load(f)


class VoxelVolumeError(Exception):
    pass


class Volume(Cuboid):
    def __init__(self, file_name_prefix: str, fov: Vec2D, step_size: float, tile_overlap: float,
                 x_axis: VoxelLinearAxis, y_axis: VoxelLinearAxis, z_axis: VoxelLinearAxis,
                 scan_strategy: ScanPlanStrategy = ParametricScanPlan(),
                 persistence: TilePersistenceStrategy = JsonifyTiles()):
        self.x_axis, self.y_axis, self.z_axis = x_axis, y_axis, z_axis
        self.file_name_prefix = file_name_prefix
        self.persistence = persistence
        self._scan_strategy = scan_strategy
        self.scan_plan = []
        self.tile_overlap = tile_overlap if 0 <= tile_overlap < 1 else DEFAULT_TILE_OVERLAP
        self._step_size = step_size
        self.tile_size = Vec3D(fov.x, fov.y, 0)
        self.tiles: Dict[Coordinate, Tile] = {}
        self.tile_count: int = 0
        self.log = get_logger(self.__class__.__name__)
        super().__init__(self.stage_limits_mm[0], self.stage_limits_mm[1])

    @property
    def scan_strategy(self):
        return self._scan_strategy

    @scan_strategy.setter
    def scan_strategy(self, strategy: ScanPlanStrategy):
        self._scan_strategy = strategy
        self.scan_plan = strategy.generate_plan(self.tiles)

    def move_to_next_tile(self, current: Tile) -> bool:
        current_index = self.scan_plan.index(current.idx)
        if current_index == len(self.scan_plan) - 1:
            raise VoxelVolumeError("No more frame stacks to move to")
        next_tile = self.scan_plan[current_index + 1]
        self.x_axis.position_mm = next_tile.pos.x
        self.y_axis.position_mm = next_tile.pos.y
        self.z_axis.position_mm = next_tile.pos.z
        # wait for the stage to move
        while self.x_axis.is_moving or self.y_axis.is_moving or self.z_axis.is_moving:
            self.log.debug(f"Waiting for stage to move to {next_tile.pos}")
        return True

    def save_tiles(self, file_path: str) -> None:
        if not self.tiles:
            raise ValueError("No tiles to save")
        self.persistence.save_tiles(self.tiles, file_path)

    def load_tiles(self, file_path: str) -> None:
        self.tiles = self.persistence.load_tiles(file_path)

    def generate_tiles(self) -> Dict[Coordinate, Tile]:
        tiles = {}
        effective_tile_width = self.tile_size.x * (1 - self.tile_overlap)
        effective_tile_height = self.tile_size.y * (1 - self.tile_overlap)

        x_tiles = int(self.size.x // effective_tile_width)
        y_tiles = int(self.size.y // effective_tile_height)

        actual_width = x_tiles * effective_tile_width
        actual_height = y_tiles * effective_tile_height

        self.tile_count = 0
        for x in range(x_tiles):
            for y in range(y_tiles):
                pos_x = x * effective_tile_width + self.min_corner.x
                pos_y = y * effective_tile_height + self.min_corner.y
                idx = (x, y, 0)
                tile = Tile(
                    idx=idx,
                    tile_number=self.tile_count,
                    pos=Vec3D(pos_x, pos_y, 0),
                    size=Vec3D(self.tile_size.x, self.tile_size.y, self.size.z),
                    step_size=self.step_size,
                    file_name_prefix=self.file_name_prefix
                )
                tiles[idx] = tile
                self.tile_count += 1

        self.tiles = tiles
        self.max_corner.x = self.min_corner.x + actual_width
        self.max_corner.y = self.min_corner.y + actual_height

        return tiles

    @property
    def step_size(self):
        return self._step_size

    @step_size.setter
    def step_size(self, step_size: int):
        self._step_size = step_size
        # make sure the size.z is a multiple of step_size
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
        # make sure the size.z is a multiple of step_size
        valid_max_z = (math.ceil((max_z - self.min_z) / self.step_size) * self.step_size) + self.min_z
        self.max_corner.z = valid_max_z

    @property
    def stage_position_mm(self) -> Vec3D:
        """Return the current position of the stage in mm"""
        return Vec3D(self.x_axis.position_mm, self.y_axis.position_mm, self.z_axis.position_mm)

    @property
    def stage_limits_mm(self) -> Tuple[Vec3D, Vec3D]:
        """Return the limits of the stage in mm"""
        return Vec3D(self.x_axis.lower_limit_mm, self.y_axis.lower_limit_mm, self.z_axis.lower_limit_mm), \
            Vec3D(self.x_axis.upper_limit_mm, self.y_axis.upper_limit_mm, self.z_axis.upper_limit_mm)

    def get_adjacent_tile(self, idx: Coordinate, direction: TileNeighbour) -> Optional[Tile]:
        if idx not in self.tiles:
            return
        x, y, z = idx
        match direction:
            case TileNeighbour.LEFT:
                return self.tiles.get((x - 1, y, z), idx)
            case TileNeighbour.RIGHT:
                return self.tiles.get((x + 1, y, z), idx)
            case TileNeighbour.UP:
                return self.tiles.get((x, y + 1, z), idx)
            case TileNeighbour.DOWN:
                return self.tiles.get((x, y - 1, z), idx)

    def __iter__(self):
        return iter(self.tiles.values())

    def __len__(self):
        return len(self.tiles)
