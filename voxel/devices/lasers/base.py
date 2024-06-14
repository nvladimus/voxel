from abc import ABC, abstractmethod
import logging

class BaseLaser(ABC):
    def __init__(self, id: str):
        self.id = id
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    @abstractmethod
    def power_mw(self) -> float:
        """Get the power of the laser in mW."""
        pass

    @power_mw.setter
    @abstractmethod
    def power_mw(self, value: float):
        """Set the power of the laser in mW."""
        pass

    @property
    @abstractmethod
    def power_setpoint_mw(self) -> float:
        """Get the power setpoint of the laser in mW."""
        pass

    @property
    @abstractmethod
    def modulation_mode(self) -> str:
        """Get the modulation mode of the laser."""
        pass

    @modulation_mode.setter
    @abstractmethod
    def modulation_mode(self, value: str):
        """Set the modulation mode of the laser."""
        pass

    @property
    @abstractmethod
    def signal_temperature_c(self) -> float:
        """Get the temperature of the laser in degrees Celsius."""
        pass

    @abstractmethod
    def status(self):
        """Get the status of the laser."""
        pass

    @abstractmethod
    def cdrh(self):
        pass

    @abstractmethod
    def enable(self):
        pass

    @abstractmethod
    def disable(self):
        pass

    @abstractmethod
    def close(self):
        pass
