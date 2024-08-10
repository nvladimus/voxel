"""Base class for all voxel devices."""
from abc import ABC, abstractmethod
import logging

LOGGING_LEVEL = logging.INFO


class VoxelDevice(ABC):
    """Base class for all voxel devices."""

    def __init__(self, id: str):
        """Initialize the device.
        :param id: The unique identifier of the device.
        :type id: str
        """
        self.id = id
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}[{self.id}]')
        self.log.setLevel(LOGGING_LEVEL)

    @abstractmethod
    def close(self):
        """Close the device."""
        pass


class DeviceConnectionError(Exception):
    """Custom exception for camera discovery errors."""
    pass
