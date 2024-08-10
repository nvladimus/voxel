# Enums for Camera Settings
from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeAlias, Dict, Union, Literal


class PixelType(Enum):
    MONO8 = auto()
    MONO10 = auto()
    MONO12 = auto()
    MONO14 = auto()
    MONO16 = auto()
    MONOSPACING = auto()
    RGB8 = auto()
    RGB10 = auto()
    RGB12 = auto()
    RGB14 = auto()


@dataclass
class PixelTypeInfo:
    repr: str | int | float
    line_interval_us: int | float


# class Binning(Enum):
#     BIN_1X1 = 1
#     BIN_2X2 = 2
#     BIN_4X4 = 4
Binning: TypeAlias = Literal[1, 2, 4]


class BitPackingMode(Enum):
    LSB = auto()
    MSB = auto()
    NONE = auto()


PixelTypeLUT: TypeAlias = Dict[PixelType, PixelTypeInfo]
BinningLUT: TypeAlias = Dict[Binning, Union[str, int]]
BitPackingModeLUT: TypeAlias = Dict[BitPackingMode, str]


class TriggerMode(Enum):
    ON = auto()
    OFF = auto()


class TriggerSource(Enum):
    INTERNAL = auto()
    EXTERNAL = auto()


class TriggerPolarity(Enum):
    RISING = auto()
    FALLING = auto()


@dataclass
class TriggerLUT:
    """Look-up table for a camera model trigger settings."""
    mode: Dict[TriggerMode, str]
    source: Dict[TriggerSource, str]
    polarity: Dict[TriggerPolarity, str]


@dataclass
class TriggerSettings:
    """Trigger settings for a camera."""
    mode: TriggerMode
    source: TriggerSource
    polarity: TriggerPolarity

    def __repr__(self):
        return f"{self.mode}, {self.source}, {self.polarity}"


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
