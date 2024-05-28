from numpy import power
import pytest

from voxel.devices.power_meter.thorlabs_pm100 import ThorlabsPowerMeter

@pytest.fixture
def pm100d():
    pm = ThorlabsPowerMeter(id="pm100d", address="USB0::0x1313::0x8078::P0022021::INSTR")
    pm.connect()
    yield pm
    pm.disconnect()

def test_power_nm(pm100d: ThorlabsPowerMeter) -> None:
    power_mw = pm100d.power_mw
    assert isinstance(power_mw, float)
    assert power_mw > 0

def test_wavelength_nm(pm100d: ThorlabsPowerMeter) -> None:
    wavelength_nm = pm100d.wavelength_nm
    assert isinstance(wavelength_nm, float)
    assert wavelength_nm > 0

def test_set_wavelength_nm(pm100d: ThorlabsPowerMeter) -> None:
    pm100d.wavelength_nm = 532
    assert pm100d.wavelength_nm == 532
