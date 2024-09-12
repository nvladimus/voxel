from enum import StrEnum
from typing import Dict

from instrument.channel import VoxelChannel


class VoxelDeviceType(StrEnum):
    CAMERA = 'camera'
    LASER = 'laser'
    FILTER = 'filter'
    LINEAR_AXIS = 'linear_axis'
    ROTATION_AXIS = 'rotation_axis'
    FLIP_MOUNT = 'flip_mount'
    TUNABLE_LENS = 'tunable_lens'
    POWER_METER = 'power_meter'
    AOTF = 'aotf'
    CHILLER = 'chiller'




class VoxelDeviceError(Exception):
    """Base class for all exceptions raised by devices."""
    pass


class DeviceConnectionError(VoxelDeviceError):
    """Custom exception for camera discovery errors."""
    pass
