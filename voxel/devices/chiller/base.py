from abc import abstractmethod

from voxel.devices.base import VoxelDevice


class VoxelChiller(VoxelDevice):
    """Base class for voxel chillers."""

    def __init__(self, name: str):
        super().__init__(name)

    @property
    @abstractmethod
    def temperature_c(self) -> float:
        """
        Get the current temperature of the chiller.
        :return: The current temperature of the chiller.
        :rtype: float
        """
        pass

    @temperature_c.setter
    @abstractmethod
    def temperature_c(self, temperature: float):
        """
        Set the temperature of the chiller.
        :param temperature: The temperature to set the chiller to.
        :type temperature: float
        """
        pass
