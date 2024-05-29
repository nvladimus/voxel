from typing import Literal
import pytest
from voxel.devices.flip_mount.thorlabs_mff101 import ThorlabsMFF101

positions: dict[str, Literal[0, 1]] = {
    'A': 0,
    'B': 1
}

@pytest.fixture
def mff101():
    fm = ThorlabsMFF101(id="flip-mount-1", address='12345678', positions=positions)
    fm.connect()
    yield fm
    fm.disconnect()

def test_position(mff101):
    assert mff101.position == 'A' # initial position
    mff101.position = 'B'
    assert mff101.position == 'B'
    mff101.position = 'A'
    assert mff101.position == 'A'

def test_toggle(mff101):
    assert mff101.position == 'A' # initial position
    mff101.toggle()
    assert mff101.position == 'B'
    mff101.toggle()
    assert mff101.position == 'A'

def test_switch_time_ms(mff101):
    assert mff101.switch_time_ms == 10.0 # default switch time
    mff101.switch_time_ms = 5.0
    assert mff101.switch_time_ms == 5.0
    mff101.switch_time_ms = 10.0
    assert mff101.switch_time_ms == 10.0

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

def test_toggle_while_transitioning(mff101):
    mff101.switch_time_ms = 0.1 * 1e3
    mff101.position = 'B'
    mff101.toggle()
    assert mff101.position == 'B'
    mff101.toggle()
    assert mff101.position == 'A'
