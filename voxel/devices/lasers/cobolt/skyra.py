import pycobolt
import logging
import sys
from sympy import symbols, solve
from voxel.devices.lasers.base import BaseLaser

# Define StrEnums if they don't yet exist.
if sys.version_info < (3, 11):
    class StrEnum(str, Enum):
        pass
else:
    from enum import StrEnum


class Cmd(StrEnum):
    LaserEnable = "l1"  # Enable(1)/Disable(0)
    LaserDisable = "l0"  # Enable(1)/Disable(0)
    EnableModulation = "em"
    ConstantPowerMode = "cp"
    EnableDigitalModulation = "sdmes 1"
    DisableDigitalModulation = "sdmes 0"
    EnableAnalogModulation = "sames 1"
    DisableAnalogModulation = "sames 0"
    PowerSetpoint = "p"
    CurrentSetpoint = "slc"


class Query(StrEnum):
    ModulationMode = "gmes?"
    AnalogModulationMode = "games?"
    DigitalModulationMode = "gdmes?"
    PowerSetpoint = "p?"


# Boolean command value that can also be compared like a boolean.
class BoolVal(StrEnum):
    OFF = "0"
    ON = "1"


MODULATION_MODES = {
    'off':     {'external_control_mode': Cmd.ConstantPowerMode,
                'digital_modulation': Cmd.DisableDigitalModulation,
                'analog_modulation': Cmd.DisableAnalogModulation},
    'analog':  {'external_control_mode': Cmd.EnableModulation,
                'digital_modulation': Cmd.DisableDigitalModulation,
                'analog_modulation': Cmd.EnableAnalogModulation},
    'digital': {'external_control_mode': Cmd.EnableModulation,
                'digital_modulation': Cmd.EnableDigitalModulation,
                'analog_modulation': Cmd.DisableAnalogModulation}
}


class LaserSkyra(CoboltLaser, BaseLaser):

    def __init__(self, port: str, prefix: str, max_power_mw: float,
                 min_current_ma: float, max_current_ma: float,
                 coefficients: dict):
        """Communicate with Skyra Cobolt laser.

                :param port: comm port for lasers.
                :param prefix: prefix specic to laser.
                :param max_power_mw: maximum power in mW
                :param coefficients: polynomial coefficients describing
                the relationship between current mA and power mW
                """

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.prefix = prefix
        self.port = port
        self.max_power_mw = max_power_mw
        self.min_current_ma = min_current_ma
        self.max_current_ma = max_current_ma
        # initialize current setpoint to min current ma
        self.current_setpoint = self.min_current_ma
        # connect() and disconnect() are inherited from CoboltLaser
        self.connect()

        # Setup curve to map power input to current mA
        self.coefficients = coefficients
        x = symbols('x')
        self.func = 0
        for order, co in self.coefficients.items():
            self.func = self.func + float(co) * x ** int(order)

    def enable(self):
        self.send_cmd(f'{self.prefix}Cmd.LaserEnable')
        self.log.info(f"laser {self.prefix} enabled")

    def disable(self):
        self.send_cmd(f'{self.prefix}Cmd.LaserDisable')
        self.log.info(f"laser {self.prefix} enabled")
    
    @property
    def power_setpoint_mw(self):
        if self.constant_current == 'ON':
            return int(round(self.func.subs(symbols('x'),
                                            self.current_setpoint)))
        else:
            # convert from watts to mw
            return self.send_cmd(f'{self.prefix}Query.PowerSetpoint') * 1000

    @power_setpoint_mw.setter
    def power_setpoint_mw(self, value: float or int):
        if self.modulation_mode != 'off':
            # solutions for laser value
            solutions = solve(self.func - value)
            for sol in solutions:
                # must be within current range
                if round(sol) in range(self.min_current_ma,
                                       self.max_current_ma):
                    # setpoint must be integer
                    self.current_setpoint = int(round(sol))
                    # set lasser current setpoint to ma value
                    self.send_cmd(f'{self.prefix}Cmd.CurrentSetpoint'
                                  f'{self.current_setpoint}')
                    return
            # if no value exists, alert user
            self.log.error(f"Cannot set laser to {value} mW because "
                           f"no current mA correlates to {value} mW")
        else:
            # convert from mw to watts
            self.send_cmd(f'{self.prefix}Cmd.PowerSetpoint {value/1000}')
        self.log.info(f"laser {self.prefix} set to {value} mW")

    @property
    def max_power_mw(self):
        if self.constant_current == 'ON':
            return int((round(self.func.subs(symbols('x'), 100), 1)))
        else:
            return int((self.max_power_mw))

    @property
    def modulation_mode(self):
        # query the laser for the modulation mode
        if self.send_cmd(f'{self.prefix}Query.ModulationMode') == BoolVal.OFF:
            return 'off'
        elif self.send_cmd(f'{self.prefix}Query.AnalogModulationMode') == BoolVal.ON:
            return 'analog'
        else:
            return 'digital'

    @modulation_mode.setter
    def modulation_mode(self, value: str):
        if value not in MODULATION_MODES.keys():
            raise ValueError("mode must be one of %r." % MODULATION_MODES.keys())
        external_control_mode = MODULATION_MODES[value]['external_control_mode']
        digital_modulation = MODULATION_MODES[value]['digital_modulation']
        analog_modulation = MODULATION_MODES[value]['analog_modulation']
        self.send_cmd(f'{self.prefix}{external_control_mode}')
        self.send_cmd(f'{self.prefix}{digital_modulation}')
        self.send_cmd(f'{self.prefix}{analog_modulation}')
        self.log.info(f"modulation mode set to {value}")

    def close(self):
        self.log.info('closing and calling disable')
        self.disable()
        if self.is_connected():
            self.disconnect()
