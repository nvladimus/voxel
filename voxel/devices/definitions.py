from enum import Enum

from .aotf import VoxelAOTF
from .camera import VoxelCamera
from .chiller import VoxelChiller
from .filter import VoxelFilter
from .flip_mount import VoxelFlipMount
from .laser import VoxelLaser
from .linear_axis import VoxelLinearAxis
from .power_meter import VoxelPowerMeter
from .rotation_axis import VoxelRotationAxis
from .tunable_lens import VoxelTunableLens


class VoxelDeviceError(Exception):
    """Base class for all exceptions raised by devices."""
    pass


class DeviceConnectionError(VoxelDeviceError):
    """Custom exception for camera discovery errors."""
    pass

class VoxelDeviceType(Enum):
    CAMERA = VoxelCamera
    LASER = VoxelLaser
    FILTER = VoxelFilter
    LINEAR_AXIS = VoxelLinearAxis
    ROTATION_AXIS = VoxelRotationAxis
    FLIP_MOUNT = VoxelFlipMount
    TUNABLE_LENS = VoxelTunableLens
    POWER_METER = VoxelPowerMeter
    AOTF = VoxelAOTF
    CHILLER = VoxelChiller

