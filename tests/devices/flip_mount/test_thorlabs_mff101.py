import time
from typing import Literal
import pytest
from voxel.devices.flip_mount import FlipMountConfig, ThorlabsMFF101

positions: dict[str, Literal[0, 1]] = {
    'A': 0,
    'B': 1,
}

mff101_config = FlipMountConfig(
    id='flip-mount-1',
    conn='37007737',
    positions={
        'A': 0,
        'B': 1,
    },
    init_pos='A',
    init_flip_time_ms=1000.0,
)

@pytest.fixture
def mff101():
    fm = ThorlabsMFF101(mff101_config)
    fm.connect()
    yield fm
    fm.disconnect()

def test_connect(mff101):
    assert mff101.inst is not None
    time.sleep(1.0)
    assert mff101.inst.get_state() == 0
    assert mff101.flip_time_ms == 500.0

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

def test_flip_time_ms(mff101):
    assert mff101.flip_time_ms == 1000.0 # default switch time
    mff101.flip_time_ms = 500.0
    assert mff101.flip_time_ms == 500.0
    mff101.flip_time_ms = 1000.0
    assert mff101.flip_time_ms == 1000.0

def test_invalid_position(mff101):
    with pytest.raises(ValueError):
        mff101.position = 'C'

def test_invalid_flip_time(mff101):
    with pytest.raises(ValueError):
        mff101.flip_time_ms = 0.0
    with pytest.raises(ValueError):
        mff101.flip_time_ms = -1.0
    with pytest.raises(ValueError):
        mff101.flip_time_ms = '5.0'
    with pytest.raises(ValueError):
        mff101.flip_time_ms = None

def test_fast_switch(mff101):
    mff101.position = 'A'
    time.sleep(2)

    cycles = 5
    switch_times = [250]
    for switch_time in switch_times:
        for _ in range(cycles):
            mff101.flip_time_ms = switch_time

            mff101.toggle()
            assert mff101.position == 'B'
            time.sleep(0.05)

            mff101.toggle()
            assert mff101.position == 'A'

    time.sleep(1.0)
    mff101.flip_time_ms = 105
    mff101.toggle()
    time.sleep(0.15)
    assert mff101.position == 'B'
