import logging
import time
from tigerasi.tiger_controller import TigerController

# constants for the ASI filter wheel

SWITCH_TIME_S = 0.1 # estimated timing

class FilterWheel:

    """Filter Wheel Abstraction from an ASI Tiger Controller."""

    def __init__(self, tigerbox: TigerController, wheel_id):
        """Connect to hardware.
      
        :param filterwheel_cfg: cfg for filterwheel
        :param tigerbox: TigerController instance.
        """
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.tigerbox = tigerbox
        self.tiger_axis = wheel_id
        # force homing of the wheel
        self.set_index(0)
        self.index = 0

    def get_index(self):
        """return all axes positions as a dict keyed by axis."""
        return self.index

    def set_index(self, index: int, wait=True):
        """Set the filterwheel index."""
        cmd_str = f"MP {index}\r\n"
        self.log.debug(f"FW{self.tiger_axis} move to index: {index}.")
        # Note: the filter wheel has slightly different reply line termination.
        self.tigerbox.send(f"FW {self.tiger_axis}\r\n", read_until=f"\n\r{self.tiger_axis}>")
        self.tigerbox.send(cmd_str, read_until=f"\n\r{self.tiger_axis}>")
        self.index = index
        # TODO: add "busy" check because tigerbox.is_moving() doesn't apply to filter wheels.
        time.sleep(SWITCH_TIME_S)