import logging
import optoICC
from optoKummenberg.tools.definitions import UnitType
from voxel.devices.tunable_lens.base import BaseTunableLens

# input constants for Optotune ICC-4C controller
# CURRENT   = 0
# OF        = 1
# XY     = 2
# FP     = 3
# UNITLESS = 4
# UNDEFINED = 5

INPUTS = {
    "current": UnitType.CURRENT,
    "of": UnitType.OF,
    "xy": UnitType.XY,
    "focal power": UnitType.FP,
    "unitless": UnitType.UNITLESS,
    "undefined": UnitType.UNDEFINED,
}

MODES = [
    "internal",  # static input mode
    "external"  # analog input mode
]


class TunableLens(BaseTunableLens):
    def __init__(self, port: str, channel: int):
        """Connect to hardware.
        """
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.icc4c = optoICC.connect(port=port)
        self.icc4c.reset(force=True)
        self.icc4c.go_pro()
        self._channel = channel
        self.tunable_lens = self.icc4c.channel[self.channel]
        # start lens in analog mode
        self._mode = "analog"
        self.tunable_lens.Analog.SetAsInput()

    @property
    def channel(self):
        """Get the tunable lens channel number."""
        return self._channel

    @property
    def mode(self):
        """Get the tunable lens control mode."""
        return self._mode

    @mode.setter
    def mode(self, mode: str):
        """Set the tunable lens control mode."""
        if mode == "external":
            self.tunable_lens.Analog.SetAsInput()
        elif mode == "internal":
            self.tunable_lens.StaticInput.SetAsInput()
        else:
            raise ValueError(f"{mode} must be {MODES}")

    @property
    def signal_temperature_c(self):
        """Get the tunable lens temperature in deg C."""
        state = {}
        state['Temperature [C]'] = self.tunable_lens.TemperatureManager.GetDeviceTemperature()
        return state

    def close(self):
        """Close the tunable lens."""
        self.icc4c.disconnect()
