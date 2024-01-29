from exa_spim_refactor.devices.lasers.laser_base import Laser
import logging
from serial import Serial


MODULATION_MODES = {
    'off' : {'external_control_mode': 'OFF', 'digital_modulation' : 'OFF'},
    'analog' : {'external_control_mode' : 'ON', 'digital_modulation' : 'OFF'},
    'digital': {'external_control_mode' : 'OFF', 'digital_modulation': 'ON'}
}

class SimulatedCombiner:

    def __init__(self, port):
        """Class for the L6CC oxxius combiner. This combiner can have LBX lasers or LCX"""

        self.ser = Serial
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._PercentageSplitStatus = 0
    @property
    def percentage_split(self):
        """Set percentage split of lasers"""

        return self._PercentageSplitStatus


    @percentage_split.setter
    def percentage_split(self, value):
        """Get percentage split of lasers"""
        if value > 100 or value < 0:
            self.log.error(f'Impossible to set percentage spilt to {value}')
            return
        self._PercentageSplitStatus = value

class SimulatedLaser(Laser):

    def __init__(self, port: Serial or str, prefix: str = '', coefficients: dict = {}):
        """Communicate with specific LBX laser in L6CC Combiner box.

                :param port: comm port for lasers.
                :param prefix: prefix specic to laser.
                """

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.prefix = prefix
        self.ser = Serial
        self._simulated_power_setpoint_m = 10.0
        self._max_power_mw = 100.0
        self._modulation_mode = 'digital'
        self._temperature = 20.0
        self._cdrh = 'ON'

    @property
    def power_setpoint_mw(self):
        return self._simulated_power_setpoint_m

    @power_setpoint_mw.setter
    def power_setpoint_mw(self, value: float):
        self._simulated_power_setpoint_m = value

    @property
    def max_power_mw(self):
        return self._max_power_mw

    @property
    def modulation_mode(self):
        return self._modulation_mode

    @modulation_mode.setter
    def modulation_mode(self, value: str):
        if value not in MODULATION_MODES.keys():
            raise ValueError("mode must be one of %r." % MODULATION_MODES.keys())
        for attribute, state in MODULATION_MODES[value].items():
            setattr(self, attribute, state)
    @property
    def temperature(self):
        return self._temperature

    def status(self):
        return []

    @property
    def cdrh(self):
        return self._cdrh

    @cdrh.setter
    def cdrh(self, value: str):
        self._cdrh = value

    def enable(self):
        pass

    def disable(self):
        pass