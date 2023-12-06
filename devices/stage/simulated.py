import logging
from base import BaseStage

class Stage(BaseStage):

    def __init__(self, tigerbox: TigerController, hardware_axis: str, instrument_axis: str):
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.tigerbox = tigerbox
        self.hardware_axis = hardware_axis.upper()
        self.instrument_axis = instrument_axis.lower()
        self.position = 0
        self.speed = 1

    def move_relative(self, position: float, wait: bool = True):
        w_text = "" if wait else "NOT "
        self.log.debug(f"Relative move by: {self.hardware_axis} and {w_text} waiting.")
        move_time_s = position/speed
        self.position += position
        if wait:
            time.sleep(move_time_s)

    def move_absolute(self, position: float, wait: bool = True):
        w_text = "" if wait else "NOT "
        self.log.debug(f"Absolute move to: {self.hardware_axis} and {w_text} waiting.")
        move_time_s = abs(self.position - position)/speed
        self.position = position
        if wait:
            time.sleep(move_time_s)

    def setup_stage_scan(self, fast_axis_start_position: float,
                               slow_axis_start_position: float,
                               slow_axis_stop_position: float,
                               frame_count: int, frame_interval_um: float,
                               strip_count: int, pattern: str,
                               retrace_speed_percent: int):

        self.position = fast_axis_start_position

    @property
    def position(self):
        return {self.hardware_axis: self.position}

    @property
    def limits(self):
        """ Get the travel limits for the specified axes.

        :return: a dict of 2-value lists, where the first element is the lower
            travel limit and the second element is the upper travel limit.
        """
        limits = {}
        # Get lower/upper limit in tigerbox frame.
        tiger_limit_lower = self.tigerbox.get_lower_travel_limit(self.hardware_axis)
        tiger_limit_upper = self.tigerbox.get_upper_travel_limit(self.hardware_axis)
        # Convert to sample frame before returning.
        sample_limit_lower = list(self._tiger_to_sample(tiger_limit_lower).values())[0]
        sample_limit_upper = list(self._tiger_to_sample(tiger_limit_upper).values())[0]
        limits[self.instrument_axis] = sorted([sample_limit_lower, sample_limit_upper])
        return limits

    @property
    def speed(self):
        return self.speed

    @speed.setter
    def speed(self, speed: float):
        self.speed = speed

    def zero_in_place(self):
        self.position = 0