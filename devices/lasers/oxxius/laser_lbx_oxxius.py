from oxxius_laser import FaultCodeField, OxxiusState,Query, Cmd, L6CCCombiner, BoolVal, LBX
from laser_base import Laser
import logging
from sympy import symbols, Eq, solve

class LaserLBXOxxius(LBX, Laser):

    def __init__(self, combiner: L6CCCombiner, prefix:str, coefficients: dict):
        """Communicate with specific LBX laser in L6CC Combiner box.

                :param combiner: L6CCCombiner object sharing comm port with individual lasers.
                :param prefix: prefix specic to laser.
                :param coefficients: polynomial coefficients describing
                the relationship between current percentage and power mw
                """

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.combiner = combiner
        self.prefix = prefix
        super(LBX, self).__init__(self.combiner.ser, self.prefix)
        # inherit from laser base class

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
    def analog_modulation(self):
        return self.external_control_mode

    @analog_modulation.setter
    def analog_modulation(self, value:str):
        self.external_control_mode = BoolVal(value)

    def status(self):
        return self.faults()



