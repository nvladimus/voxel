from enum import Enum, auto
from typing import Dict, Optional
from tigerasi.tiger_controller import TigerController

from ..base import LinearAxisDimension

type AxisMap = Dict[LinearAxisDimension, str]


class ASIAxisRole(Enum):
    FAST_AXIS = auto()
    SLOW_AXIS = auto()

# TODO: Should the tigerbox class be a subclass of the tiger controller class?
# or should it act as a wrapper around the tiger controller class?
# TODO: Should the ASITigerBox class be stored in the devices/linear_axis/asi/ directory
# or outside of the linear_axis directory since it will be used by different types of devices?

class ASITigerBox(TigerController):
    def __init__(self, port: str, axis_map: AxisMap):
        super().__init__(port)
        self.axis_map = self._sanitize_axis_map(axis_map)
        self.step_shoot_scan_roles: Dict[LinearAxisDimension, ASIAxisRole] = {}
        self.stage_scan_roles: Dict[LinearAxisDimension, ASIAxisRole] = {}
        self.log.debug(f'Axis map: {self.axis_map}')

    def get_axis_position(self, axis: LinearAxisDimension) -> float | None:
        box_axis: str = self.axis_map[axis]
        position_dict = super().get_position(box_axis)
        try:
            return float(position_dict[box_axis])
        except KeyError:
            self.log.error(f'Could not get position for axis {axis}')
        except Exception as e:
            self.log.error(f'Error getting position for axis {axis}: {e}')

    def set_axis_position(self, axis: LinearAxisDimension, position: float, wait: bool = True) -> None:
        box_axis: str = self.axis_map[axis]
        kwds = {
            'wait': wait,
            box_axis: position
            }
        super().set_position(**kwds)

    def get_axis_limits(self, axis: LinearAxisDimension) -> tuple[float, float] | None:
        box_axis: str = self.axis_map[axis]
        lower_limit_dict = super().get_lower_travel_limit(box_axis)
        upper_limit_dict = super().get_upper_travel_limit(box_axis)
        try:
            lower_limit = float(lower_limit_dict[box_axis])
            upper_limit = float(upper_limit_dict[box_axis])
            return lower_limit, upper_limit
        except KeyError:
            self.log.error(f'Could not get limits for axis {axis}')
        except Exception as e:
            self.log.error(f'Error getting limits for axis {axis}: {e}')

    def set_axis_limits(self, axis: LinearAxisDimension, lower_limit: float, upper_limit: float) -> None:
        box_axis: str = self.axis_map[axis]
        lower_limit_kwds = {
            'wait': True,
            box_axis: lower_limit
            }
        upper_limit_kwds = {
            'wait': True,
            box_axis: upper_limit
            }
        super().set_lower_travel_limit(**lower_limit_kwds)
        super().set_upper_travel_limit(**upper_limit_kwds)

    def get_axis_speed(self, axis: LinearAxisDimension) -> float | None:
        box_axis: str = self.axis_map[axis]
        speed_dict = super().get_speed(box_axis)
        try:
            return float(speed_dict[box_axis])
        except KeyError:
            self.log.error(f'Could not get speed for axis {axis}')
        except Exception as e:
            self.log.error(f'Error getting speed for axis {axis}: {e}')

    def set_axis_speed(self, axis: LinearAxisDimension, speed_mm_s: float) -> None:
        box_axis: str = self.axis_map[axis]
        kwds = {
            'wait': True,
            box_axis: speed_mm_s
        }
        super().set_speed(**kwds)

    def get_axis_acceleration(self, axis: LinearAxisDimension) -> float | None:
        box_axis: str = self.axis_map[axis]
        acceleration_dict = super().get_acceleration(box_axis)
        try:
            return float(acceleration_dict[box_axis])
        except KeyError:
            self.log.error(f'Could not get acceleration for axis {axis}')
        except Exception as e:
            self.log.error(f'Error getting acceleration for axis {axis}: {e}')

    def set_axis_acceleration(self, axis: LinearAxisDimension, acceleration_ms: float) -> None:
        box_axis: str = self.axis_map[axis]
        kwds = {
            'wait': True,
            box_axis: acceleration_ms
        }
        super().set_acceleration(**kwds)

    def get_axis_home_position(self, axis: LinearAxisDimension) -> float | None:
        box_axis: str = self.axis_map[axis]
        home_position_dict = super().get_home(box_axis)
        try:
            return float(home_position_dict[box_axis])
        except KeyError:
            self.log.error(f'Could not get home position for axis {axis}')
        except Exception as e:
            self.log.error(f'Error getting home position for axis {axis}: {e}')

    def set_axis_home_position(self, axis: LinearAxisDimension, home_position_mm: float) -> None:
        box_axis: str = self.axis_map[axis]
        kwds = {
            'wait': True,
            box_axis: home_position_mm
        }
        super().set_home(**kwds)

    def set_axis_home_position_in_place(self, axis: LinearAxisDimension) -> None:
        box_axis: str = self.axis_map[axis]
        super().set_home(box_axis)

    def home_axis(self, axis: LinearAxisDimension) -> None:
        box_axis: str = self.axis_map[axis]
        super().home(box_axis)

    def zero_in_place(self, axis: LinearAxisDimension) -> None:
        box_axis: str = self.axis_map[axis]
        super().zero_in_place(box_axis)

    def is_axis_moving(self, axis: LinearAxisDimension) -> bool:
        box_axis: str = self.axis_map[axis]
        return super().is_axis_moving(box_axis)

    def set_axis_backlash(self, axis: LinearAxisDimension, backlash_mm) -> None:
        box_axis: str = self.axis_map[axis]
        kwds = {
            'wait': True,
            box_axis: backlash_mm
        }
        super().set_axis_backlash(**kwds)

    def update_step_shoot_scan_roles(
            self, dimension: LinearAxisDimension, role: ASIAxisRole) -> None:
        self.step_shoot_scan_roles[dimension] = role

    def update_stage_scan_roles(
            self, dimension: LinearAxisDimension, role: ASIAxisRole) -> None:
        self.stage_scan_roles[dimension] = role

    def setup_step_shoot_scan(
            self,
            slow_scan_dimension: LinearAxisDimension,
            start_mm: float,
            stop_mm: float,
            step_size_um: float,
            overshoot_time_ms: int = 0,
            overshoot_factor: float = 1.0,
            ) -> None:
        line_count = int((stop_mm - start_mm) / step_size_um)
        self.update_step_shoot_scan_roles(slow_scan_dimension, ASIAxisRole.SLOW_AXIS)
        for axis in self.axis_map:
            if axis != slow_scan_dimension:
                self.update_step_shoot_scan_roles(axis, ASIAxisRole.FAST_AXIS)
        # pick the first axis that is not the slow scan dimension to be the fast axis
        fast_axis = [k for k, v in self.step_shoot_scan_roles.items() if v == ASIAxisRole.FAST_AXIS][0]
        super().setup_scan(
            fast_axis=self.axis_map[fast_axis],
            slow_axis=self.axis_map[slow_scan_dimension],
        )
        super().scanv(
            scan_start_mm=start_mm,
            scan_stop_mm=stop_mm,
            line_count=line_count,
            overshoot_time_ms=overshoot_time_ms,
            overshoot_factor=overshoot_factor,
        )

    # TODO: Implement this method to configure a stage scan
    # How do we deal with the fact that both the fast and slow axes are needed for a stage scan?
    # stage_scan_roles dictionary might perhaps store this information
    # How do roles influence the scan configuration?
    # How does stage_scan_configuration impact step_shoot_scan_configuration if using the same tigerbox and/or axes?
    def setup_stage_scan(
            self,
            fast_scan_dimension: LinearAxisDimension,
            fast_axis_start_position: float,
            slow_axis_start_position: float,
            slow_axis_stop_position: float,
            frame_count: int,
            frame_interval_um: float,
            strip_count: int,
            pattern: str,
    ):
        self.update_stage_scan_roles(fast_scan_dimension, ASIAxisRole.FAST_AXIS)
        for axis in self.axis_map:
            if axis != fast_scan_dimension:
                self.update_stage_scan_roles(axis, ASIAxisRole.SLOW_AXIS)


    def _validate_stage_scan_roles(self) -> bool:
        if ASIAxisRole.FAST_AXIS not in self.stage_scan_roles.values():
            self.log.error('Fast axis role is not assigned')
            return False
        if ASIAxisRole.SLOW_AXIS not in self.stage_scan_roles.values():
            self.log.error('Slow axis role is not assigned')
            return False
        return True

    @staticmethod
    def _sanitize_axis_map( axis_map: AxisMap) -> AxisMap:
        return {k: v.upper() for k, v in axis_map.items()}