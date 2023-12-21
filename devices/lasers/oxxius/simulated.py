from oxxius_laser import BoolVal
from devices.lasers.laser_base import Laser
import logging
from sympy import symbols, solve
from serial import Serial


MODULATION_MODES = {
    'off' : {'external_control_mode': BoolVal.OFF, 'digital_modulation' :BoolVal.OFF},
    'analog' : {'external_control_mode' :BoolVal.ON, 'digital_modulation' :BoolVal.OFF},
    'digital': {'external_control_mode' :BoolVal.OFF, 'digital_modulation': BoolVal.ON}
}


class LaserLBXOxxius(Laser):

    def __init__(self, port: Serial or str, prefix: str):
        """Communicate with specific LBX laser in L6CC Combiner box.

                :param port: comm port for lasers.
                :param prefix: prefix specic to laser.
                """

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.prefix = prefix

    @property
    def power_setpoint_mw(self):
        return self.simulated_power_setpoint_m

    @property
    def max_power_mw(self):
        pass

    @property
    def modulation_mode(self):
        pass

    @property
    def temperature(self):
        pass

    def status(self):
        pass

    def cdrh(self):
        pass

    def enable(self):
        pass

    def disable(self):
        pass
