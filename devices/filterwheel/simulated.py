import logging
import time
from .base import BaseFilterWheel

SWITCH_TIME_S = 0.1 # estimated timing

class FilterWheel(BaseFilterWheel):

    def __init__(self, filter_list: dict):
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.filter_list = filter_list
        # force homing of the wheel
        self.set_index(next(key for key, value in self.filter_list.items() if value == 0))
        # store simulated index internally
        self.index = 0

    def get_index(self):
        return next(key for key, value in self.filter_list.items() if value == self.index)

    def set_index(self, filter_name: str, wait=True):
        """Set the filterwheel index."""
        self.index = self.filter_list[filter_name]
        time.sleep(SWITCH_TIME_S)