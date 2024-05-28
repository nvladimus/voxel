from abc import ABC, abstractmethod

class BasePowerMeter(ABC):
    """
    Abstract base class for a voxel power meter.
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Connect the power meter.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect the power meter.
        """
        pass

    @property
    @abstractmethod
    def power_mw(self) -> float:
        """
        Returns:
        float: The power in milliwatts.
        """
        pass

    @property
    @abstractmethod
    def wavelength_nm(self) -> float:
        """
        Returns:
        float: The wavelength in nanometers.
        """
        pass

    @wavelength_nm.setter
    @abstractmethod
    def wavelength_nm(self, wavelength: float):
        """
        Parameters:
        wavelength (float): The new wavelength in nanometers.
        """
        pass
