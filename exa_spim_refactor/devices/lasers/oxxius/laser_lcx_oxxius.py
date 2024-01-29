from oxxius_laser import LCX
from devices.lasers.laser_base import Laser
import logging
from serial import Serial

class LaserLCXOxxius(LCX, Laser):

    def __init__(self,  port: Serial or str, prefix:str):
        """Communicate with specific LBX laser in L6CC Combiner box.

                :param port: comm port for lasers.
                :param prefix: prefix specic to laser.
                """
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.prefix = prefix
        super(LCX, self).__init__(port, self.prefix)
        # inherit from laser device_widget class

    @property
    def power_setpoint_mw(self):
        return self.power_setpoint

    @power_setpoint_mw.setter
    def power_setpoint_mw(self, value: float or int):
        self.power_setpoint = value

    @property
    def max_power_mw(self):
        return self.max_power

    @property
    def modulation_mode(self):
        raise AttributeError

    def status(self):
        return self.status()

    def cdrh(self):
        raise AttributeError


