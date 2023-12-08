import logging
import time
from tigerasi.tiger_controller import TigerController

# constants for the ASI filter wheel

SWITCH_TIME_S = 0.1 # estimated timing

class FilterWheel:

    """Filter Wheel Abstraction from an ASI Tiger Controller."""

    def __init__(self, tigerbox: TigerController, wheel_id, filter_list: dict):
        """Connect to hardware.
      
        :param filterwheel_cfg: cfg for filterwheel
        :param tigerbox: TigerController instance.
        """
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.tigerbox = tigerbox
        self.tiger_axis = wheel_id
        self.filter_list = filter_list
        # force homing of the wheel
        self.set_index(next(key for key, value in self.filter_list.items() if value == 0))
        # ASI wheel has no get_index() function so store this internally
        self.index = 0

    def get_index(self):
        """return all axes positions as a dict keyed by axis."""
        return next(key for key, value in self.filter_list.items() if value == self.index)

    def set_index(self, filter_name: str, wait=True):
        """Set the filterwheel index."""
        self.index = self.filter_list[filter_name]
        cmd_str = f"MP {self.index}\r\n"
        self.log.debug(f"FW{self.tiger_axis} move to index: {self.index}.")
        # Note: the filter wheel has slightly different reply line termination.
        self.tigerbox.send(f"FW {self.tiger_axis}\r\n", read_until=f"\n\r{self.tiger_axis}>")
        self.tigerbox.send(cmd_str, read_until=f"\n\r{self.tiger_axis}>")
        # TODO: add "busy" check because tigerbox.is_moving() doesn't apply to filter wheels.
        time.sleep(SWITCH_TIME_S)