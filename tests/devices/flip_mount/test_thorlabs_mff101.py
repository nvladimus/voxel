import time
from typing import Literal
import pytest
from voxel.devices.flip_mount.thorlabs_mff101 import ThorlabsMFF101

positions: dict[str, Literal[0, 1]] = {
    'A': 0,
    'B': 1
}

@pytest.fixture
def mff101():
    fm = ThorlabsMFF101(id="flip-mount-1", address='37007737', positions=positions)
    fm.connect()
    yield fm
    fm.disconnect()

def test_connect(mff101):
    assert mff101.inst is not None
    time.sleep(1.0)
    assert mff101.inst.get_state() == 0
    assert mff101.switch_time_ms == 1000.0

def test_position(mff101):
    assert mff101.position == 'A' # initial position
    mff101.position = 'B'
    assert mff101.position == 'B'
    mff101.position = 'A'
    assert mff101.position == 'A'

def test_toggle(mff101):
    mff101.position = 'A'
    assert mff101.position == 'A'

    mff101.toggle()
    assert mff101.position == 'B'

    time.sleep(0.5)

    mff101.toggle()
    assert mff101.position == 'A'

def test_switch_time_ms(mff101):
    assert mff101.switch_time_ms == 1000.0 # default switch time
    mff101.switch_time_ms = 500.0
    assert mff101.switch_time_ms == 500.0
    mff101.switch_time_ms = 1000.0
    assert mff101.switch_time_ms == 1000.0

def test_invalid_position(mff101):
    with pytest.raises(ValueError):
        mff101.position = 'C'

def test_invalid_switch_time(mff101):
    with pytest.raises(ValueError):
        mff101.switch_time_ms = 0.0
    with pytest.raises(ValueError):
        mff101.switch_time_ms = -1.0
    with pytest.raises(ValueError):
        mff101.switch_time_ms = '5.0'
    with pytest.raises(ValueError):
        mff101.switch_time_ms = None

def test_fast_switch(mff101):
    mff101.position = 'A'
    time.sleep(2)

    cycles = 5
    switch_times = [250]
    for switch_time in switch_times:
        for _ in range(cycles):
            mff101.switch_time_ms = switch_time

            mff101.toggle()
            assert mff101.position == 'B'
            time.sleep(0.05)

            mff101.toggle()
            assert mff101.position == 'A'

    time.sleep(1.0)
    mff101.switch_time_ms = 105
    mff101.toggle()
    time.sleep(0.15)
    assert mff101.position == 'B'
