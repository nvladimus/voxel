from logging import info
from pdb import pm
import time
from numpy import power
import pytest

from voxel.devices.power_meter.thorlabs_pm100 import ThorlabsPowerMeter

import logging

logging.basicConfig(level=logging.DEBUG)

STRESS_TEST_MINUTES = 120

@pytest.fixture
def pm100d():
    pm = ThorlabsPowerMeter(id="pm100d", address="USB0::0x1313::0x8078::P0008860::INSTR")
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

@pytest.mark.stress
def test_extended_data_collection(pm100d) -> None:
    """
    Stress test for the power meter device. Collect data for extended period of time.
    To run this test, use the following command:
        pytest ./test_thorlabs_pm100.py -m "stress" -s -o log_cli=true -o log_cli_level=INFO
    command should be run from the tests/devices/power_meter directory.
    """
    pm100d.log.info(f"\nStarting stress test for {STRESS_TEST_MINUTES} minutes")
    start_time = time.time()
    duration = STRESS_TEST_MINUTES * 60 # in seconds
    while time.time() - start_time < duration:
        power = pm100d.power_mw
        pm100d.log.info(f"Power: {power} mW")
        assert power >= 0 and power <= 1000
        time.sleep(1)  # wait for 1 second before the next data collection
