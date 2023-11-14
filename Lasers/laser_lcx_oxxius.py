from oxxius_laser import FaultCodeField, OxxiusState,Query, Cmd, L6CCCombiner, BoolVal, LCX
from laser_base import Laser
import logging

class LaserLCXOxxius(LCX, Laser):

    def __init__(self, combiner: L6CCCombiner, prefix:str):
        """Communicate with specific LBX laser in L6CC Combiner box.

                :param combiner: L6CCCombiner object sharing comm port with individual lasers.
                :param prefix: prefix specic to laser.
                """
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.combiner = combiner
        self.prefix = prefix
        super(LCX, self).__init__(self.combiner.ser, self.prefix)
        # inherit from laser base class

    @property
    def digital_modulation(self):
        raise AttributeError

    @property
    def analog_modulation(self):
        raise AttributeError

    @property
    def external_control_mode(self):
        raise AttributeError

    def status(self):
        return self.status()

    def cdrh(self):
        raise AttributeError


