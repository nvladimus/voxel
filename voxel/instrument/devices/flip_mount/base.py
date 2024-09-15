from abc import abstractmethod

from utils.descriptors.deliminated_property import deliminated_property
from voxel.instrument.device import VoxelDevice


class VoxelFlipMount(VoxelDevice):
    """Base class for Voxel flip mounts.
    :param name: Name of the flip mount
    :type name: str
    """

    def __init__(self, name: str):
        super().__init__(name)

    @property
    @abstractmethod
    def position(self) -> str:
        """Position of the flip mount.
        :return: Name of the current position
        :rtype: str
        """
        pass

    @position.setter
    @abstractmethod
    def position(self, position_name: str, wait=False):
        """Set the flip mount to a specific position
        :param position_name: Name of the position to move to
        :param wait: Wait for the flip mount to finish flipping. Default: False
        """
        pass

    @abstractmethod
    def toggle(self, wait=True):
        """Toggle the flip mount position \n
        :param wait: Wait for the flip mount to finish flipping. Default: True
        :type wait: bool
        """
        pass

    @abstractmethod
    def wait(self):
        """Wait for the flip mount to finish flipping."""
        pass

    @deliminated_property()
    @abstractmethod
    def flip_time_ms(self) -> float:
        """Time it takes to flip the mount in milliseconds. \n
        :return: Time in milliseconds
        :rtype: float
        """
        pass

    @flip_time_ms.setter
    @abstractmethod
    def flip_time_ms(self, time_ms: float):
        """Set the time it takes to flip the mount in milliseconds. \n
        :param time_ms: Time in milliseconds
        :type time_ms: float
        """
        pass