# Enums for Camera Settings
from dataclasses import dataclass
from enum import Enum, auto, IntEnum
from typing import TypeAlias, Dict, Union, Literal, Set
import numpy as np

from numpy.typing import NDArray

from voxel.devices.utils.geometry import Vec2D

# constants
BYTES_PER_MB = 1_000_000

# Type aliases
VoxelFrame: TypeAlias = NDArray[np.uint8 | np.uint16]

CMD: TypeAlias = Union[str, int, float]


class Binning(IntEnum):
    X1 = 1
    X2 = 2
    X4 = 4
    X8 = 8


BinningLUT: TypeAlias = Dict[Binning, CMD]


class PixelType(IntEnum):
    MONO8 = 8
    MONO10 = 10
    MONO12 = 12
    MONO14 = 14
    MONO16 = 16

    @property
    def numpy_dtype(self) -> np.dtype:
        return np.uint8 if self == PixelType.MONO8 else np.uint16


PixelTypeLUT: TypeAlias = Dict[PixelType, CMD]


class BitPackingMode(Enum):
    LSB = auto()
    MSB = auto()
    NONE = auto()


BitPackingModeLUT: TypeAlias = Dict[BitPackingMode, str]


@dataclass
class ROI:
    origin: Vec2D
    size: Vec2D

    def __repr__(self):
        return f"Origin = {self.origin}, Size = {self.size}"


@dataclass
class AcquisitionState:
    frame_index: int
    input_buffer_size: int
    output_buffer_size: int
    dropped_frames: int
    frame_rate_fps: float
    data_rate_mbs: float

    def __repr__(self):
        return (
            f"Frame Index              = {self.frame_index}\n"
            f"Input Buffer Size       = {self.input_buffer_size}\n"
            f"Output Buffer Size    = {self.output_buffer_size}\n"
            f"Dropped Frames       = {self.dropped_frames}\n"
            f"Frame Rate [fps]       = {self.frame_rate_fps}\n"
            f"Data Rate [MB/s]      = {self.data_rate_mbs}\n"
        )
