import pytest

from voxel.devices.power_meter.simulated import SimulatedPowerMeter

@pytest.fixture
def power_meter():
    pm = SimulatedPowerMeter(id="simulated-pm", wavelength_nm = 538)
    pm.connect()
    yield pm
    pm.disconnect()

def test_power_nm(power_meter):
    assert power_meter.power_mw == pytest.approx(500, abs=50)

def test_wavelength_nm(power_meter) -> None:
    assert power_meter.wavelength_nm == 538

def test_set_wavelength_nm(power_meter) -> None:
    power_meter.wavelength_nm = 532
    assert power_meter.wavelength_nm == 532

def test_disconnect(power_meter) -> None:
    power_meter.disconnect()
    with pytest.raises(Exception):
        power_meter.power_mw
    with pytest.raises(Exception):
        power_meter.wavelength_nm
    with pytest.raises(Exception):
        power_meter.wavelength_nm = 532