from voxel.devices.linear_axis import (
    BaseLinearAxis,
    LinearAxisDimension,
    LinearAxisRole,
)
from ..base import BaseScanningLinearAxis
from .tigerbox import ASITigerBox


class ASITigerLinearAxis(BaseLinearAxis):
    def __init__(
        self,
        id: str,
        dimension: LinearAxisDimension,
        role: LinearAxisRole,
        tigerbox: ASITigerBox,
    ):
        super().__init__(id, dimension, role)
        self._tigerbox = tigerbox

    @property
    def position_mm(self) -> float | None:
        return self._tigerbox.get_axis_position(self.dimension)

    @position_mm.setter
    def position_mm(self, position: float) -> None:
        self._tigerbox.set_axis_position(self.dimension, position)

    @property
    def limits_mm(self) -> tuple[float, float] | None:
        return self._tigerbox.get_axis_limits(self.dimension)

    @limits_mm.setter
    def limits_mm(self, limits: tuple[float, float]) -> None:
        self._tigerbox.set_axis_limits(self.dimension, *limits)

    @property
    def speed_mm_s(self) -> float | None:
        return self._tigerbox.get_axis_speed(self.dimension)

    @speed_mm_s.setter
    def speed_mm_s(self, speed_mm_s: float) -> None:
        self._tigerbox.set_axis_speed(self.dimension, speed_mm_s)

    @property
    def acceleration_ms(self) -> float | None:
        return self._tigerbox.get_axis_acceleration(self.dimension)

    @acceleration_ms.setter
    def acceleration_ms(self, acceleration_ms: float) -> None:
        self._tigerbox.set_axis_acceleration(self.dimension, acceleration_ms)

    @property
    def is_moving(self) -> bool:
        return self._tigerbox.is_axis_moving(self.dimension)

    @property
    def home_position_mm(self) -> float | None:
        return self._tigerbox.get_axis_home_position(self.dimension)

    @home_position_mm.setter
    def home_position_mm(self, home_position_mm: float) -> None:
        self._tigerbox.set_axis_home_position(self.dimension, home_position_mm)

    def set_home_in_place(self) -> None:
        return self._tigerbox.set_axis_home_position_in_place(self.dimension)

    def home(self) -> None:
        return self._tigerbox.home_axis(self.dimension)

    def zero_in_place(self) -> None:
        return self._tigerbox.zero_in_place(self.dimension)

    def set_backlash_mm(self, backlash_mm: float) -> None:
        self._tigerbox.set_axis_backlash(self.dimension, backlash_mm)


# TODO: Is this the best way to add extra functionality (scanning capabiity) to a BaseLinearAxis class?
class ASITigerScanningLinearAxis(ASITigerLinearAxis, BaseScanningLinearAxis):
    def __init__(
        self,
        id: str,
        dimension: LinearAxisDimension,
        role: LinearAxisRole,
        tigerbox: ASITigerBox,
    ):
        super().__init__(id, dimension, role, tigerbox)

    def configure_scan(
        self, start_mm: float, stop_mm: float, step_size_um: float
    ) -> None:
        return self._tigerbox.setup_step_shoot_scan(
            self.dimension, start_mm, stop_mm, step_size_um
        )
