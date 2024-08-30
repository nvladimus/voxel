from abc import abstractmethod
from enum import StrEnum
from typing import Any, Dict

from ..base import VoxelDevice


class TunableLensControlMode(StrEnum):
    """Tunable lens control modes."""
    INTERNAL = "internal"
    EXTERNAL = "external"


class VoxelTunableLens(VoxelDevice):

    @property
    @abstractmethod
    def mode(self) -> TunableLensControlMode:
        """Get the tunable lens control mode."""
        pass

    @mode.setter
    @abstractmethod
    def mode(self, mode: TunableLensControlMode):
        """Set the tunable lens control mode.
        :param mode: one of "internal" or "external".
        :type mode: str
        """
        pass

    @property
    @abstractmethod
    def temperature_c(self) -> float:
        """Get the temperature in deg C."""
        pass

    @abstractmethod
    def log_metadata(self) -> Dict[str, Any]:
        """Log metadata about the tunable lens."""
        pass
