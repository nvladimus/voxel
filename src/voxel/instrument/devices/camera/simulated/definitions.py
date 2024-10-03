from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from voxel.instrument.devices.camera import Binning, PixelType


class TriggerMode(StrEnum):
    ON = 'On'
    OFF = 'Off'


class TriggerSource(StrEnum):
    INTERNAL = 'Internal'
    EXTERNAL = 'External'


class TriggerPolarity(StrEnum):
    RISINGEDGE = 'Rising Edge'
    FALLINGEDGE = 'Falling Edge'


@dataclass
class TriggerSettings:
    """Trigger settings for a camera."""
    mode: Optional[TriggerMode]
    source: Optional[TriggerSource]
    polarity: Optional[TriggerPolarity]

    def __repr__(self):
        return f"{self.mode}, {self.source}, {self.polarity}"

    def dict(self):
        return {
            'mode': self.mode,
            'source': self.source,
            'polarity': self.polarity
        }


class SimulatedCameraSettings:
    """Settings for a simulated camera."""
    Binning = Binning
    PixelType = PixelType
    TriggerMode = TriggerMode
    TriggerSource = TriggerSource
    TriggerPolarity = TriggerPolarity
    TriggerSettings = TriggerSettings