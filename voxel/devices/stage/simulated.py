import logging
import time
from voxel.devices.stage.base import BaseStage
import random

class Stage(BaseStage):

    def __init__(self, hardware_axis: str, instrument_axis: str):
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.hardware_axis = hardware_axis.upper()
        self.instrument_axis = instrument_axis.lower()
        # TODO change this, but self.id for consistency in lookup
        self.id = self.instrument_axis
        self._position = 0
        self._speed = 1.0

    def move_relative(self, position: float, wait: bool = True):
        w_text = "" if wait else "NOT "
        self.log.info(f"relative move by: {self.hardware_axis}={position} mm and {w_text}waiting.")
        move_time_s = position/self._speed
        self.move_end_time_s = time.time() + move_time_s
        self._position += position
        while time.time() < self.move_end_time_s:
            time.sleep(0.01)

    def move_absolute(self, position: float, wait: bool = True):
        w_text = "" if wait else "NOT "
        self.log.info(f"absolute move to: {self.hardware_axis}={position} mm and {w_text}waiting.")
        move_time_s = abs(self._position - position)/self._speed
        self.move_end_time_s = time.time() + move_time_s
        self._position = position
        while time.time() < self.move_end_time_s:
            time.sleep(0.01)

    def setup_stage_scan(self, fast_axis_start_position: float,
                               slow_axis_start_position: float,
                               slow_axis_stop_position: float,
                               frame_count: int, frame_interval_um: float,
                               strip_count: int, pattern: str,
                               retrace_speed_percent: int):

        self._position = fast_axis_start_position

    @property
    def position(self):
        self._position = random.randint(0,100)
        return {self.instrument_axis: self._position}

    @property
    def speed_mm_s(self):
        return self._speed

    @speed_mm_s.setter
    def speed_mm_s(self, speed_mm_s: float):
        self._speed = speed_mm_s

    def is_axis_moving(self):
        if time.time() < self.move_end_time_s:
            return True
        else:
            return False

    def zero_in_place(self):
        self._position = 0