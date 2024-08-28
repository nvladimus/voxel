from typing import Dict, TypeAlias

from tigerasi.device_codes import TTLIn0Mode, TTLOut0Mode, ScanPattern
from tigerasi.tiger_controller import TigerController

from devices.linear_axis.definitions import LinearAxisDimension, ScanState

AxisMap: TypeAlias = Dict[str, str]  # axis id -> hardware_axis
DimensionsMap: TypeAlias = Dict[LinearAxisDimension, str]  # LinearAxisDimension -> axis id

STEPS_PER_UM = 10


class ASITigerBox:
    def __init__(self, port: str):
        self.box = TigerController(port)
        self.axis_map = {}
        self.dimensions_map = {}
        self.scan_state = ScanState.IDLE
        self.log = self.box.log
        self.log.debug(f'Axis map: {self.axis_map}')
        self.build_config = self.box.get_build_config()

    @property
    def hardware_axes(self) -> list[str]:
        return self.box.ordered_axes

    def register_axis(self, axis_id: str, hardware_axis: str, dimension: LinearAxisDimension):
        # there can be only one X, Y, Z axis but multiple N axes
        if hardware_axis not in self.hardware_axes:
            raise ValueError(f"Hardware axis {hardware_axis} not found in the connected device.")
        if dimension == LinearAxisDimension.N:
            self.axis_map[axis_id] = hardware_axis
            return
        if dimension in self.dimensions_map:
            raise ValueError(f"Only one {dimension.name} dimension is allowed. "
                             f"Axis dimension {dimension} already registered under "
                             f"axis ID {self.dimensions_map[dimension]}")
        if axis_id in self.axis_map:
            raise ValueError(f"Axis ID {axis_id} already registered under hardware axis {self.axis_map[axis_id]}")
        self.axis_map[axis_id] = hardware_axis
        self.dimensions_map[dimension] = axis_id

    def deregister_axis(self, axis_id: str):
        if axis_id in self.axis_map:
            self.axis_map.pop(axis_id)
        for dimension, axis in self.dimensions_map.items():
            if axis == axis_id:
                self.dimensions_map.pop(dimension)

    def close(self):
        if not self.axis_map:
            if self.scan_state == ScanState.SCANNING:
                self.box.stop_scan()
            self.box.ser.close()

    def get_axis_position(self, axis_id: str) -> float:
        box_axis = self.axis_map[axis_id]
        steps = float(self.box.get_position(box_axis)[box_axis])
        return steps / (STEPS_PER_UM * 1000)  # convert to mm

    def move_absolute_mm(self, axis_id: str, position_mm: float) -> None:
        self.box.move_absolute(**{self.axis_map[axis_id]: round(position_mm * 1000 * STEPS_PER_UM, 1), 'wait': True})

    def get_axis_limits(self, axis_id: str) -> tuple[float, float]:
        box_axis = self.axis_map[axis_id]
        lower = float(self.box.get_lower_travel_limit(box_axis)[box_axis])
        upper = float(self.box.get_upper_travel_limit(box_axis)[box_axis])
        return lower, upper

    def get_upper_travel_limit(self, axis_id: str) -> float:
        return float(self.box.get_upper_travel_limit(self.axis_map[axis_id])[self.axis_map[axis_id]])

    def get_lower_travel_limit(self, axis_id: str) -> float:
        return float(self.box.get_lower_travel_limit(self.axis_map[axis_id])[self.axis_map[axis_id]])

    def set_upper_travel_limit_in_place(self, axis_id: str):
        self.box.set_upper_travel_limit(self.axis_map[axis_id])

    def set_lower_travel_limit_in_place(self, axis_id: str):
        self.box.set_lower_travel_limit(self.axis_map[axis_id])

    def set_upper_travel_limit(self, axis_id: str, limit: float):
        self.box.set_upper_travel_limit(**{self.axis_map[axis_id]: limit, 'wait': True})

    def set_lower_travel_limit(self, axis_id: str, limit: float):
        self.box.set_lower_travel_limit(**{self.axis_map[axis_id]: limit, 'wait': True})

    def set_axis_limits(self, axis_id: str, lower_limit: float, upper_limit: float) -> None:
        self.set_upper_travel_limit(axis_id, upper_limit)
        self.set_lower_travel_limit(axis_id, lower_limit)

    def get_axis_speed(self, axis_id: str) -> float:
        box_axis = self.axis_map[axis_id]
        return float(self.box.get_speed(box_axis)[box_axis])

    def set_axis_speed(self, axis_id: str, speed_mm_s: float) -> None:
        box_axis = self.axis_map[axis_id]
        self.box.set_speed(**{box_axis: speed_mm_s, 'wait': True})

    def get_axis_acceleration(self, axis_id: str) -> float:
        box_axis = self.axis_map[axis_id]
        return float(self.box.get_acceleration(box_axis)[box_axis])

    def set_axis_acceleration(self, axis_id: str, acceleration_ms: float) -> None:
        box_axis = self.axis_map[axis_id]
        self.box.set_acceleration(**{box_axis: acceleration_ms, 'wait': True})

    def zero_in_place(self, axis_id: str) -> None:
        self.box.zero_in_place(self.axis_map[axis_id])

    def is_axis_moving(self, axis_id: str) -> bool:
        return self.box.are_axes_moving(self.axis_map[axis_id])[self.axis_map[axis_id]]

    # def get_axis_backlash(self, axis_id: str) -> float:
    #     box_axis = self.axis_map[axis_id]
    #     return float(self.box.get_axis_backlash(box_axis)[box_axis])

    def set_axis_backlash(self, axis_id: str, backlash_mm: float) -> None:
        box_axis = self.axis_map[axis_id]
        self.box.set_axis_backlash(**{box_axis: backlash_mm, 'wait': True})

    def setup_step_shoot_scan(self, axis_id: str, step_size_um: float) -> bool:
        """Queue a single-axis relative move of the specified amount."""
        if not self.has_all_stage_axes or self.dimensions_map[axis_id] != LinearAxisDimension.Z:
            return False
        try:
            if self.scan_state == ScanState.SCANNING:
                self.box.stop_scan()
            step_size_steps = step_size_um * STEPS_PER_UM
            self.box.reset_ring_buffer()
            self.box.setup_ring_buffer(self.axis_map[axis_id])
            self.box.queue_buffered_move(**{self.axis_map[axis_id]: step_size_steps})
            # TTL mode dictates whether ring buffer move is relative or absolute.
            self.box.set_ttl_pin_modes(TTLIn0Mode.MOVE_TO_NEXT_REL_POSITION,
                                       TTLOut0Mode.PULSE_AFTER_MOVING,
                                       aux_io_mode=0, aux_io_mask=0,
                                       aux_io_state=0)
            self.scan_state = ScanState.CONFIGURED
            return True
        except Exception as e:
            self.log.error(f"Failed to setup step-and-shoot scan: {e}")
            return False

    def setup_stage_scan(self, fast_axis_start_position: float,
                         slow_axis_start_position: float,
                         slow_axis_stop_position: float,
                         frame_count: int, frame_interval_um: float,
                         strip_count: int,
                         retrace_speed_percent: int,
                         pattern: ScanPattern = ScanPattern.SERPENTINE
                         ):
        """Configure a stage scan orchestrated by the device hardware.

        This function sets up the outputting of <tile_count> output pulses
        spaced out by every <tile_interval_um> encoder counts.

        :param fast_axis_start_position:
        :param slow_axis_start_position:
        :param slow_axis_stop_position:
        :param frame_count: number of TTL pulses to fire.
        :param frame_interval_um: distance to travel between firing TTL pulses.
        :param strip_count: number of stacks to collect along the slow axis.
        :param retrace_speed_percent: speed of the retrace in percent of the scan speed.
        :param pattern:
        """
        # :param fast_axis: the axis to move along to take tile images.
        # :param slow_axis: the axis to move across to take tile stacks.
        # TODO: if position is unspecified, we should set is as
        #  "current position" from hardware.
        # Get the axis id in machine coordinate frame.

        assert 100 >= retrace_speed_percent > 0
        fast_axis = self.axis_map[LinearAxisDimension.X]
        slow_axis = self.axis_map[LinearAxisDimension.Y]

        # Stop any existing scan. Apply machine coordinate frame scan params.
        self.log.debug(f"fast axis start: {fast_axis_start_position},"
                       f"slow axis start: {slow_axis_start_position}")

        self.box.setup_scan(fast_axis, slow_axis, pattern)
        self.box.scanr(scan_start_mm=fast_axis_start_position,
                       pulse_interval_um=frame_interval_um,
                       num_pixels=frame_count,
                       retrace_speed_percent=retrace_speed_percent)
        self.box.scanv(scan_start_mm=slow_axis_start_position,
                       scan_stop_mm=slow_axis_stop_position,
                       line_count=strip_count)

    def start_scan(self, wait: bool = True) -> None:
        if self.scan_state == ScanState.CONFIGURED:
            self.box.start_scan(wait)
            self.scan_state = ScanState.SCANNING

    def stop_scan(self, wait: bool = True) -> None:
        self.box.stop_scan(wait)
        self.scan_state = ScanState.IDLE

    @property
    def has_all_stage_axes(self) -> bool:
        return all(axis in self.dimensions_map for axis in LinearAxisDimension)

    @staticmethod
    def _sanitize_axis_map(axis_map: AxisMap) -> AxisMap:
        return {k: v.upper() for k, v in axis_map.items()}

    def wait(self) -> None:
        self.box.wait()
