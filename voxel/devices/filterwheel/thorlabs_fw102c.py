import logging
import time
from pylablib.devices import Thorlabs
from voxel.devices.filterwheel.base import BaseFilterWheel

# constants for the Thorlabs FW102C filter wheel

SWITCH_TIME_S = 0.1 # estimated timing


class FilterWheel(BaseFilterWheel):

    """Filter Wheel Abstraction from an ASI Tiger Controller."""

    def __init__(self, port: str, filters: dict):
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        try:
            self.filter_wheel = Thorlabs.serial.FW(conn=port)
        except:
            self.log.debug(f'{port} is not a valid thorabs'
                           f'filter wheel connection')
            raise ValueError(f'could not find power meter with id {port}')
        self.filters = filters
        self.number_of_filters = self.filter_wheel.get_pcount()
        if len(self.filters) > self.number_of_filters:
            raise ValueError(f'too many filters. must'
                             f'be < {self.number_of_filters}'
        # force homing of the wheel
        self.filter = next(key for key, value in self.filters.items() if value == 0)
        # force slow moving by default
        self.filter_wheel.set_speed_mode("low")

    @property
    def filter(self):
        # returns the filter position staring at 1
        filter_position = self.filter_wheel.get_position()
        return next(key for key, value in self.filters.items() if value == filter_positin)

    @filter.setter
    def filter(self, filter_name: str):
        self.filter_wheel.set_position(self.filters[filter_name])
        self.log.info(f'filter wheel moved to filter {filter_name}')
        time.sleep(SWITCH_TIME_S)

    def close(self):
        self.filter_wheel.close()
        self.log.info(f'filter wheel closed on COIM {port}')