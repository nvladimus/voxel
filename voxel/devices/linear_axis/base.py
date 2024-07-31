from abc import abstractmethod
from enum import Enum, auto
from typing import Tuple

from pytools import F
from voxel.devices.base import VoxelDevice


class LinearAxisDimension(Enum):
    X = auto()
    Y = auto()
    Z = auto()


class LinearAxisRole(Enum):
    TILING = auto()
    FAST_SCANNING = auto()
    SLOW_SCANNING = auto()


class BaseLinearAxis(VoxelDevice):
    def __init__(self, id: str, dimension: LinearAxisDimension, role: LinearAxisRole):
        super().__init__(id)
        self.dimension: LinearAxisDimension = dimension
        self.type: LinearAxisRole = role

    @property
    @abstractmethod
    def position_mm(self) -> float | None:
        """Current position in mm"""
        pass

    @position_mm.setter
    @abstractmethod
    def position_mm(self, position: float) -> None:
        """Move to position in mm"""
        pass

    @property
    @abstractmethod
    def limits_mm(self) -> Tuple[float, float] | None:
        """A tuple of (min, max) position limits in mm
        rtype: Tuple[float, float]
        """
        pass

    @property
    @abstractmethod
    def speed_mm_s(self) -> float:
        """Current speed in mm/s"""
        pass

    @speed_mm_s.setter
    @abstractmethod
    def speed_mm_s(self, speed: float) -> None:
        """Set speed in mm/s"""
        pass

    @property
    @abstractmethod
    def acceleration_ms(self) -> float:
        """Current acceleration in m/s^2"""
        pass

    @acceleration_ms.setter
    @abstractmethod
    def acceleration_ms(self, acceleration: float) -> None:
        """Set acceleration in m/s^2"""
        pass

    @property
    @abstractmethod
    def is_moving(self) -> bool:
        """Whether the axis is moving"""
        pass

    @property
    @abstractmethod
    def home_position_mm(self) -> float:
        """Home position in mm"""
        pass

    @home_position_mm.setter
    @abstractmethod
    def home_position_mm(self, position: float) -> None:
        """Set home position in mm"""
        pass

    @abstractmethod
    def home(self) -> None:
        """Move to home position"""
        pass

    @abstractmethod
    def zero_in_place(self) -> None:
        """Set current position as zero"""
        pass

    @abstractmethod
    def set_backlash_mm(self, backlash_mm: float) -> None:
        """Set backlash in mm"""
        pass


class BaseScanningLinearAxis:
    @abstractmethod
    def configure_scan(
        self,
        start_mm: float,
        stop_mm: float,
        retrace_speed: float,
        **kwargs,
    ) -> None:
        """Configure scanning parameters
        :param start_mm: start position in mm
        :param stop_mm: stop position in mm
        :param retrace_speed: retrace speed in mm/s
        """
        pass

    @abstractmethod
    def start_scan(self) -> None:
        """Start scanning"""
        pass

    @abstractmethod
    def stop_scan(self) -> None:
        """Stop scanning"""
        pass


class BaseSweepingLinearAxis:
    @abstractmethod
    def configure_sweep(
        self,
        start_mm: float,
        stop_mm: float,
        speed: float,
        **kwargs,
    ) -> None:
        """Configure sweeping parameters
        :param start_mm: start position in mm
        :param stop_mm: stop position in mm
        :param speed: speed in mm/s
        """
        pass

    @abstractmethod
    def start_sweep(self) -> None:
        """Start sweeping"""
        pass

    @abstractmethod
    def stop_sweep(self) -> None:
        """Stop sweeping"""
        pass
