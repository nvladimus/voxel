from abc import ABC, abstractmethod

class BasePowerMeter(ABC):
    """
    Abstract base class for a voxel power meter.
    """

    def __init__(self, wavelength_nm: float):
        """
        Initialize the power meter with a specific wavelength.

        Parameters:
        wavelength_nm (float): The wavelength in nanometers.
        """
        self.wavelength_nm = wavelength_nm

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
