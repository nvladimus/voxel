from oxxius_laser import LCX
from voxel.devices.lasers.base import BaseLaser
import logging
from serial import Serial
from voxel.descriptors.deliminated_property import DeliminatedProperty

class LaserLCXOxxius(LCX, BaseLaser):

    def __init__(self,  port: Serial or str, prefix:str):
        """Communicate with specific LBX laser in L6CC Combiner box.

                :param port: comm port for lasers.
                :param prefix: prefix specic to laser.
                """
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.port = port
        self.prefix = prefix
        super(LCX, self).__init__(port, self.prefix)
        # inherit from laser device_widgets class

        self.set_max_power()

    @DeliminatedProperty(minimum=0, maximum=float('inf'))
    def power_setpoint_mw(self):
        return float(self.power_setpoint)

    @power_setpoint_mw.setter
    def power_setpoint_mw(self, value: float or int):
        self.power_setpoint = value

    @property
    def modulation_mode(self):
        raise AttributeError

    def status(self):
        return self.status()

    def cdrh(self):
        raise AttributeError

    def close(self):
        self.disable()
        if self.port.is_open:
            self.port.close()

    def set_max_power(self):
        type(self).power_setpoint_mw.maximum = self.max_power


