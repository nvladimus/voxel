from oxxius_laser import BoolVal, LBX
from devices.lasers.laser_base import Laser
import logging
from sympy import symbols, solve
from serial import Serial


MODULATION_MODES = {
    'off' : {'external_control_mode': BoolVal.OFF, 'digital_modulation':BoolVal.OFF},
    'analog' : {'external_control_mode':BoolVal.ON, 'digital_modulation':BoolVal.OFF},
    'digital': {'external_control_mode' :BoolVal.OFF, 'digital_modulation':BoolVal.ON}
}

class LaserLBXOxxius(LBX, Laser):

    def __init__(self, port: Serial or str, prefix:str, coefficients: dict):
        """Communicate with specific LBX laser in L6CC Combiner box.

                :param port: comm port for lasers.
                :param prefix: prefix specic to laser.
                :param coefficients: polynomial coefficients describing
                the relationship between current percentage and power mw
                """

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.prefix = prefix
        super(LBX, self).__init__(port, self.prefix)
        # inherit from laser device_widgets class

        # Setup curve to map power input to current percentage
        self.coefficients = coefficients
        x = symbols('x')
        self.func = 0
        for order, co in self.coefficients.items():
            self.func = self.func + float(co) * x ** int(order)

    @property
    def power_setpoint_mw(self):
        if self.constant_current == BoolVal.ON:
            return round(self.func.subs(symbols('x'), self.current_setpoint), 1)
        else:
            return self.power_setpoint

    @power_setpoint_mw.setter
    def power_setpoint_mw(self, value: float or int):

        if self.constant_current == BoolVal.ON:
            solutions = solve(self.func - value)  # solutions for laser value
            for sol in solutions:
                if round(sol) in range(0, 101):
                    self.current_setpoint = round(sol, 1)
                    return
            # If no value exists, alert user
            self.log.error(f"Cannot set laser to {value}mW because "
                           f"no current percent correlates to {value} mW")
        else:
            self.power_setpoint = value

    @property
    def max_power_mw(self):
        if self.constant_current == BoolVal.ON:
            return round(self.func.subs(symbols('x'), 100), 1)
        else:
            return self.max_power

    @property
    def modulation_mode(self):
        if self.external_control_mode == BoolVal.ON:
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



