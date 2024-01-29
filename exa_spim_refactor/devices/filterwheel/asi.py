import logging
import time
from tigerasi.tiger_controller import TigerController
from .base import BaseFilterWheel

# constants for the ASI filter wheel

SWITCH_TIME_S = 0.1 # estimated timing

class FilterWheel(BaseFilterWheel):

    """Filter Wheel Abstraction from an ASI Tiger Controller."""

    def __init__(self, port: str, id, filters: dict):
        """Connect to hardware.
      
        :param filterwheel_cfg: cfg for filterwheel
        :param tigerbox: TigerController instance.
        """
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.tigerbox = TigerController(port)
        self.tiger_axis = id
        self.filters = filters
        # force homing of the wheel
        self.set_filter(next(key for key, value in self.filters.items() if value == 0))
        # ASI wheel has no get_index() function so store this internally
        self.index = 0

    def get_filter(self):
        return next(key for key, value in self.filters.items() if value == self.index)

    def set_filter(self, filter_name: str, wait=True):
        """Set the filterwheel index."""
        self.index = self.filters[filter_name]
        cmd_str = f"MP {self.index}\r\n"
        self.log.info(f'setting filter to {filter_name}')
        # Note: the filter wheel has slightly different reply line termination.
        self.tigerbox.send(f"FW {self.tiger_axis}\r\n", read_until=f"\n\r{self.tiger_axis}>")
        self.tigerbox.send(cmd_str, read_until=f"\n\r{self.tiger_axis}>")
        # TODO: add "busy" check because tigerbox.is_moving() doesn't apply to filter wheels.
        time.sleep(SWITCH_TIME_S)