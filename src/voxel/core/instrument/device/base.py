"""Voxel Compatible Devices."""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

from pytools import F


from voxel.core.utils.log_config import get_component_logger


class VoxelDeviceType(StrEnum):
    CAMERA = "camera"
    LENS = "lens"
    LASER = "laser"
    FILTER = "filter"
    FILTER_WHEEL = "filter_wheel"
    LINEAR_AXIS = "linear_axis"
    ROTATION_AXIS = "rotation_axis"
    FLIP_MOUNT = "flip_mount"
    TUNABLE_LENS = "tunable_lens"
    POWER_METER = "power_meter"
    AOTF = "aotf"
    CHILLER = "chiller"
    WRITER = "writer"
    FILE_TRANSFER = "transfer"


class VoxelDeviceError(Exception):
    """Base class for all exceptions raised by devices."""

    pass


class VoxelDeviceConnectionError(VoxelDeviceError):
    """Custom exception for camera discovery errors."""

    pass


class VoxelDevice(ABC):
    """Base class for all voxel devices."""

    def __init__(self, device_type: VoxelDeviceType, name: str = "Device"):
        """Initialize the device.
        :param name: The unique identifier of the device.
        :type name: str
        """
        self.name = name
        self.log = get_component_logger(self)
        self.daq_task = None
        self.daq_channel = None
        self.device_type: VoxelDeviceType = device_type

    def apply_settings(self, settings: dict):
        """Apply settings to the device."""
        for key, value in settings.items():
            try:
                setattr(self, key, value)
            except AttributeError:
                self.log.error(f"Instance '{self.name}' has no attribute '{key}'")
            except Exception as e:
                self.log.error(f"Error setting '{key}' for '{self.name}': {str(e)}")
                raise
        self.log.info(f"Applied settings to '{self.name}'")

    @abstractmethod
    def close(self):
        """Close the device."""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}[{self.name}]"

    # @abstractmethod
    def log_metadata(self) -> dict[str, Any]:
        """Log metadata about the device."""
        pass
