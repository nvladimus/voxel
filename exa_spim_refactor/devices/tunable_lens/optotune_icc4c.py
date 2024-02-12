import logging
from devices.tunable_lens.base import BaseTunableLens
import optoICC

# constants for Optotune ICC-4C controller

class TunableLens(BaseTunableLens):

    def __init__(self, port: str, channel: int):
        """Connect to hardware.

        :param tigerbox: TigerController instance.
        :param hardware_axis: stage hardware axis.
        """
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.icc4c = optoICC.connect(port=port)
        self.icc4c.reset(force=True)
        self.icc4c.go_pro()
        self.channel = channel
        self._mode = None
        self.tunable_lens = self.icc4c.channel[self.channel]

    @property
    def mode(self):
        """Get the tunable lens control mode."""
        return self._mode

    @mode.setter
    def mode(self, mode: str):
        """Set the tunable lens control mode."""

        if mode == 'external':
            max_diopter = self.tunable_lens.LensCompensation.GetMaxDiopter()
            min_diopter = self.tunable_lens.LensCompensation.GetMinDiopter()
            self.tunable_lens.Analog.SetVoltages_LUT([0, 10])
            self.tunable_lens.Analog.SetValues_LUT([min_diopter, max_diopter])
            self.tunable_lens.Analog.SetAsInput()
            self._mode = 'external'
        elif mode == 'internal':
            self.tunable_lens.StaticInput.SetAsInput()
            self._mode = 'internal'
        else:
            raise ValueError("mode must be one of external or internal")

    @property
    def temperature(self):
        """Get the temperature in deg C."""
        return self.tunable_lens.TemperatureManager.GetDeviceTemperature()[self.channel]