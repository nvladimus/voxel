from typing import Optional
import pyvisa as visa

from voxel.devices.power_meter.base import BasePowerMeter

class ThorlabsPowerMeter(BasePowerMeter):
    def __init__(self, id: str, address: str) -> None:
        super().__init__(id)
        self.address = address
        self.inst: Optional[visa.resources.Resource] = None

    def connect(self):
        rm = visa.ResourceManager()
        try:
            self.inst = rm.open_resource(self.address)
            self.log.info(f"Connection to {self.address} successful")
        except visa.VisaIOError as e:
            self.log.error(f"Could not connect to {self.address}: {e}")
            raise
        except Exception as e:
            self.log.error(f"Unknown error: {e}")
            raise

    def disconnect(self) -> None:
        if self.inst is not None:
            self.inst.close()
            self.inst = None
            self.log.info(f"Disconnected from {self.address}")
        else:
            self.log.warning(f"Already disconnected from {self.address}")

    def _check_connection(self):
        if self.inst is None:
            raise Exception(f"Device {self.id} is not connected")

    @property
    def power_mw(self) -> float:
        self._check_connection()
        return float(self.inst.query("MEAS:POW?")) # type: ignore

    @property
    def wavelength_nm(self) -> float:
        self._check_connection()
        return float(self.inst.query('SENS:CORR:WAV?')) # type: ignore

    @wavelength_nm.setter
    def wavelength_nm(self, wavelength: float) -> None:
        self._check_connection()
        self.inst.write(f"SENS:CORR:WAV {wavelength}") # type: ignore
        self.log.info(f"{self.id} - Set wavelength to {wavelength} nm")
