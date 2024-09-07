from abc import abstractmethod
from typing import Optional

from ..base import VoxelDevice
from ..definitions import VoxelDeviceType


class VoxelLaser(VoxelDevice):
    """Base class for all voxel laser devices."""

    def __init__(self, name: str):
        super().__init__(name)
        self.device_type = VoxelDeviceType.LASER

    def __repr__(self):
        return (
            f"voxel id:         {self.name}\n"
            f"Wavelength:       {self.wavelength}\n"
            f"Power setpoint:   {self.power_setpoint_mw} mW\n"
            f"Power:            {self.power_mw} mW\n"
            f"Temperature:      {self.temperature_c} °C"
        )

    @abstractmethod
    def enable(self):
        """Turn on the laser"""
        pass

    @abstractmethod
    def disable(self):
        """Turn off the laser"""
        pass

    @property
    @abstractmethod
    def wavelength(self):
        """Wavelength of laser"""
        pass

    @property
    @abstractmethod
    def power_setpoint_mw(self) -> float:
        """
        The power setpoint is the target power that the laser is trying to achieve.

        :return: The power setpoint in mW.
        :rtype: float
        """
        pass

    @power_setpoint_mw.setter
    @abstractmethod
    def power_setpoint_mw(self, value: float) -> None:
        """
        Set the power setpoint for the laser in mW.

        :param value: The power setpoint in mW.
        :type value: float
        :rtype: None
        """
        pass

    @property
    @abstractmethod
    def power_mw(self) -> float:
        """
        Get the actual power of the laser in mW.

        :return: The power in mW.
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def temperature_c(self) -> Optional[float]:
        """
        Get the main temperature of the laser in degrees Celsius.

        :return: The temperature in degrees Celsius.
        :rtype: float
        """
        pass
