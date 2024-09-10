"""Base class for all voxel devices."""
from abc import ABC, abstractmethod
from typing import Optional

from voxel.instrument.definitions import VoxelDeviceType
from voxel.utils.logging import get_logger


class VoxelDevice(ABC):
    """Base class for all voxel devices."""

    def __init__(self, name: Optional[str] = None):
        """Initialize the device.
        :param name: The unique identifier of the device.
        :type name: str
        """
        self.name = name
        self.device_type: Optional[VoxelDeviceType] = None
        self.log = get_logger(f'{self.__class__.__name__}[{self.name}]')

        self.daq_task = None
        self.daq_channel = None

    @abstractmethod
    def close(self):
        """Close the device."""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}[{self.name}]"
