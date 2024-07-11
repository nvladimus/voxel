"""Base class for all voxel devices."""
from abc import ABC, abstractmethod
import logging

class VoxelDevice(ABC):
    """Base class for all voxel devices."""

    def __init__(self, id: str):
        self.id = id
        self.log = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

    @abstractmethod
    def close(self):
        """Close the device."""
        pass

