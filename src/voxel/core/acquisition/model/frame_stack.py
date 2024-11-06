import math
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

from voxel.core.instrument import VoxelInstrument
from voxel.core.instrument.channel import VoxelChannel
from voxel.core.utils.geometry.vec import Vec2D, Vec3D


@dataclass
class FrameStack:
    idx: Vec2D
    pos: Vec3D
    size: Vec3D
    z_step_size: float
    channels: list[str]
    settings: Optional[dict[str, dict[str, Any]]] = None

    @property
    def frame_count(self):
        return math.ceil(self.size.z / self.z_step_size)

    def to_dict(self):
        return {
            "idx": self.idx.to_str(),
            "pos": self.pos.to_str(),
            "size": self.size.to_str(),
            "z_step_size": self.z_step_size,
            "channels": self.channels,
            "settings": self.settings,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FrameStack":
        return cls(
            idx=Vec2D.from_str(data["idx"]),
            pos=Vec3D.from_str(data["pos"]),
            size=Vec3D.from_str(data["size"]),
            z_step_size=data["z_step_size"],
            channels=data["channels"],
            settings=data.get("settings"),
        )


def get_frame_stack_size_mb(frame_stack: FrameStack, instrument: VoxelInstrument) -> float:
    def get_size_mb(channel: "VoxelChannel") -> float:
        frame_size_mb = (
            channel.camera.frame_size_px.x
            * channel.camera.frame_size_px.y
            * np.dtype(channel.writer.data_type).itemsize
            / 1024**2
        )
        return frame_size_mb * frame_stack.frame_count

    total_size_mb = 0
    for channel_name in frame_stack.channels:
        try:
            total_size_mb += get_size_mb(instrument.channels[channel_name])
        except KeyError:
            raise ValueError(f"Channel '{channel_name}' not found in instrument channels")
    return total_size_mb
