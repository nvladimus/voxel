"""Base class for all voxel devices."""
from abc import ABC, abstractmethod
from typing import Optional

from voxel.instrument._definitions import VoxelDeviceType
from voxel.utils.logging import get_logger


class VoxelDevice(ABC):
    """Base class for all voxel devices."""

    def __init__(self, name: Optional[str] = None):
        """Initialize the device.
        :param name: The unique identifier of the device.
        :type name: str
        """
        self.name = name
        self.daq_task = None
        self.daq_channel = None
        self.device_type: Optional[VoxelDeviceType] = None
        self.log = get_logger(f'{self.__class__.__name__}[{self.name}]')

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
