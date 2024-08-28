"""Base class for all voxel devices."""
import logging
from abc import ABC, abstractmethod


class VoxelDevice(ABC):
    """Base class for all voxel devices."""

    def __init__(self, id: str):
        self.id = id
        self.log = logging.getLogger(f"{self.__class__.__name__}[{self.id}]")

    @abstractmethod
    def close(self):
        """Close the device."""
        pass

    def __str__(self):
        return self.__repr__()
