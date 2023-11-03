from oxxius_laser import OxxiusLaser, FaultCodeField, OxxiusState,Query, Cmd
from exa-spim-refactor.Lasers import Laser
from enum import Enum, IntEnum

class ModulationMode (IntEnum):
    DIGITAL_MODULATION = 1
    ANALOG_MODUALTION = 0



class OxxiusDriver(OxxiusLaser,Laser):

    def __init__(self, port,
                 prefix=None,
                 intensity_mode = 'current',
                 modulation_mode: str = None,
                 laser_driver_control_mode: str = None,
                 external_control: str = None):
        super(OxxiusDriver, self).__init__(port, prefix, intensity_mode,
                                           modulation_mode, laser_driver_control_mode,
                                           external_control)
    @property
    def setpoint(self):
         return self.get_setpoint()

    @setpoint.setter
    def setpoint(self, value):
        return self.set_setpoint(value)

    @property
    def max_setpoint(self):
        return self.get_max_setpoint()

    @property
    def modulation_mode(self):
        value = self.get(Query.ModulationMode)
        return ModulationMode(value).name

    @modulation_mode.setter
    def modulation_mode(self, value):
        return self.set(Cmd.ModulationMode[value])

    def status(self):
        return self.state()
    

