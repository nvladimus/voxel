import math
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, TypeAlias, Tuple

import numpy as np

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

Coordinate: TypeAlias = Tuple[int, int]


@dataclass
class Tile:
    idx: Coordinate
    pos: Vec3D
    size: Vec3D
    step_size: float
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

    def __str__(self):
        return f"Tile {self.tile_number} at {self.pos} with size {self.size}"

    def __repr__(self):
        return f"Tile {self.tile_number} at {self.pos} with size {self.size}"

    def to_dict(self):
        return {
            "idx": self.idx,
            "pos": self.pos.to_dict(),
            "size": self.size.to_dict(),
            "step_size": self.step_size,
            "tile_number": self.tile_number,
            "channel_names": self.channel_names,
            "settings": self.settings
        }

    @classmethod
    def from_dict(cls, data):
        def get_coords(idx: str) -> Tuple[int, int]:
            split = idx.split(",")
            return int(split[0]), int(split[1])

        return cls(
            idx=get_coords(data["idx"]),
            pos=Vec3D.from_dict(data["pos"]),
            size=Vec3D.from_dict(data["size"]),
            step_size=data["step_size"],
            tile_number=data["tile_number"],
            channel_names=data["channel_names"],
            settings=data["settings"]
        )


TilesSet: TypeAlias = Dict[Coordinate, Tile]
