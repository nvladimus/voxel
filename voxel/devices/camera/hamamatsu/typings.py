from dataclasses import dataclass
from enum import IntEnum
from typing import TypeAlias, Dict


class SensorMode(IntEnum):
    """The sensor mode of the camera."""
    AREA = 1
    LINE = 3
    TDI = 4
    TDI_EXTENDED = 10
    PROGRESSIVE = 12
    SPLITVIEW = 14
    DUALLIGHTSHEET = 16
    PHOTONNUMBERRESOLVING = 18
    WHOLELINES = 19


SensorModeLUT: TypeAlias = Dict[SensorMode, int]


class ReadoutDirection(IntEnum):
    """The readout direction of the camera."""
    FORWARD = 1
    BACKWARD = 2
    BYTRIGGER = 3
    DIVERGE = 5
    FORWARDBIDIRECTION = 6
    REVERSEBIDIRECTION = 7


ReadoutDirectionLUT: TypeAlias = Dict[ReadoutDirection, int]


class TriggerMode(IntEnum):
    NORMAL = 1
    PIV = 3
    START = 6


TriggerModeLUT: TypeAlias = Dict[TriggerMode, int]


class TriggerSource(IntEnum):
    """The trigger source of the camera."""
    INTERNAL = 1
    EXTERNAL = 2
    SOFTWARE = 3
    MASTERPULSE = 4


TriggerSourceLUT: TypeAlias = Dict[TriggerSource, int]


class TriggerPolarity(IntEnum):
    """The trigger polarity of the camera."""
    NEGATIVE = 1
    POSITIVE = 2


TriggerPolarityLUT: TypeAlias = Dict[TriggerPolarity, int]


class TriggerActive(IntEnum):
    """The type of trigger event that will be used to trigger the camera."""
    EDGE = 1
    LEVEL = 2
    SYNCREADOUT = 3
    POINT = 4

    # TODO: Rewrite descriptions for each value
    # TODO: Figure out the usefulness of descriptions and whether they should be included in the final implementation
    @classmethod
    def description(cls, value=None):
        if not value:
            return 'Specifies the type of trigger event to be used'
        if value == cls.EDGE:
            return 'The camera will be triggered on the edge of the trigger signal'
        if value == cls.LEVEL:
            return 'The camera will be triggered on the level of the trigger signal'
        if value == cls.SYNCREADOUT:
            return 'The camera will be triggered on the readout of the trigger signal'
        if value == cls.POINT:
            return 'The camera will be triggered on the point of the trigger signal'


TriggerActiveLUT: TypeAlias = Dict[TriggerActive, int]


@dataclass
class TriggerSettings:
    mode: TriggerMode
    source: TriggerSource
    polarity: TriggerPolarity
    active: TriggerActive

    def dict(self):
        return {
            'mode': self.mode,
            'source': self.source,
            'polarity': self.polarity,
            'active': self.active
        }
