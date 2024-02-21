from stradus import StradusLaser, BoolVal
from voxel.devices.lasers.base import BaseLaser
import logging
from serial import Serial

MODULATION_MODES = {
    'off' : {'external_control': BoolVal.OFF, 'digital_modulation':BoolVal.OFF},
    'analog' : {'external_control':BoolVal.ON, 'digital_modulation':BoolVal.OFF},
    'digital': {'external_control' :BoolVal.OFF, 'digital_modulation':BoolVal.ON}
}

class LaserStradusVortran(StradusLaser, BaseLaser):

    def __init__(self, port: Serial):
        """Communicate with stradus laser.

                :param port: comm port for lasers.
                """

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        super(StradusLaser, self).__init__(port)
        # inherit from laser device_widgets class


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
        if self.external_control == BoolVal.ON:
            return 'analog'
        elif self.digital_modulation == BoolVal.ON:
            return 'digital'
        else:
            return 'off'

    @modulation_mode.setter
    def modulation_mode(self, value: str):
        if value not in MODULATION_MODES.keys():
            raise ValueError("mode must be one of %r." % MODULATION_MODES.keys())
        for attribute, state in MODULATION_MODES[value].items():
            setattr(self, attribute, state)

    def status(self):
        return self.faults()



