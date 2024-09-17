import math
from typing import Tuple, List

from instrument.channel import VoxelChannel
from voxel.utils.geometry.cuboid import Cuboid
from voxel.utils.geometry.vec import Vec3D, Vec2D, Plane
from voxel.utils.logging import get_logger
from .tile import Tile, Tiles

DEFAULT_TILE_OVERLAP = 0.15


class VoxelVolumeError(Exception):
    pass


class Volume(Cuboid):
    def __init__(self, step_size: float, stage_limits_mm: Tuple[Vec3D, Vec3D], tile_overlap: float) -> None:
        self.log = get_logger(self.__class__.__name__)
        super().__init__(stage_limits_mm[0], stage_limits_mm[1])
        self.tile_overlap = tile_overlap if 0 <= tile_overlap < 1 else DEFAULT_TILE_OVERLAP
        self._step_size = step_size

    def generate_tiles(self, channels: List[VoxelChannel], name_prefix: str) -> Tiles:
        # all channels must have the same fov
        fov = channels[0].fov_um
        for channel in channels:
            if channel.fov_um != fov:
                raise VoxelVolumeError("Unable to generate tiles with channels of different FOV")
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
                idx = (x, y)
                tile = Tile(
                    idx=idx,
                    tile_number=tile_count,
                    pos=Vec3D(pos_x, pos_y, 0),
                    size=Vec3D(fov.x, fov.y, self.size.z),
                    step_size=self.step_size,
                    file_name_prefix=name_prefix,
                    channel_names=[channel.name for channel in channels]
                )
                tiles[idx] = tile
                tile_count += 1

        self.max_corner.x = self.min_corner.x + actual_width
        self.max_corner.y = self.min_corner.y + actual_height

        return tiles

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
