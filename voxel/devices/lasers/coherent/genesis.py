from voxel.devices.lasers import BaseLaser
from voxel.devices.lasers.coherent import HOPSDevice


class GenesisLaser(HOPSDevice, BaseLaser):
    def __init__(self, id: str, conn: str):
        HOPSDevice.__init__(self, conn)
        BaseLaser.__init__(self, id)
        self.initialize()

    @property
    def power_mw(self):
        """Get the current power of the laser."""
        return float(self.send_command("?P"))

    @power_mw.setter
    def power_mw(self, value: float):
        """Set the power of the laser."""
        self.send_command(f'PCMD={value}')

    @property
    def power_setpoint_mw(self):
        """Get the current power setpoint of the laser."""
        return float(self.send_command("?PCMD"))

    @property
    def modulation_mode(self) -> str:
        """Get the modulation mode of the laser."""
        return ''

    @modulation_mode.setter
    def modulation_mode(self, value: str):
        pass

    @property
    def signal_temperature_c(self) -> float:
        """Get the temperature of the laser in degrees Celsius."""
        return 0.0

    def status(self):
        """Get the status of the laser."""
        pass

    def cdrh(self):
        pass

    def enable(self):
        pass

    def disable(self):
        pass
