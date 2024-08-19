from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Dict, Optional


class BitPackingMode(StrEnum):
    LSB = 'LSB'
    MSB = 'MSB'
    NONE = 'None'


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


@dataclass
class TriggerSettingsLUT:
    """Look-up table for a camera model trigger settings."""
    mode: Dict[TriggerMode, str]
    source: Dict[TriggerSource, str]
    polarity: Dict[TriggerPolarity, str]
