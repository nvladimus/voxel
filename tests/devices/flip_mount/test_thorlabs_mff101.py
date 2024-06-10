import time
import pytest
from voxel.devices.flip_mount import FlipMountConfig, ThorlabsMFF101
from voxel.devices.flip_mount.thorlabs_mff101 import FLIP_TIME_RANGE

CONN = '37007737'
POSITIONS = {
    'A': 0,
    'B': 1,
}
INIT_POS = 'A'
INIT_FLIPTIME = 1000

@pytest.fixture
def mff101():
    fm = ThorlabsMFF101(
            id='flip-mount-1',
            conn=CONN,
            positions=POSITIONS,
            init_pos=INIT_POS,
            init_flip_time_ms=INIT_FLIPTIME
        )
    yield fm
    fm.disconnect()

def test_connect(mff101):
    assert mff101._inst is not None
    mff101.wait()
    assert mff101.position == INIT_POS
    assert mff101.flip_time_ms == INIT_FLIPTIME

def test_disconnect(mff101):
    mff101.disconnect()
    assert mff101._inst is None

def test_position(mff101):
    mff101.wait()
    assert mff101.position == 'A'

    mff101.position = 'B'
    mff101.wait()
    assert mff101.position == 'B'

    mff101.position = 'A'
    mff101.wait()
    assert mff101.position == 'A'

def test_toggle(mff101):
    mff101.wait()
    assert mff101.position == 'A'

    mff101.toggle(wait=True)
    assert mff101.position == 'B'

    mff101.toggle(wait=True)
    assert mff101.position == 'A'

def test_invalid_position(mff101):
    with pytest.raises(ValueError):
        mff101.position = 'C'

def test_flip_time_ms(mff101):
    assert mff101.flip_time_ms == 1000.0 # default switch time
    mff101.flip_time_ms = 500.0
    assert mff101.flip_time_ms == 500.0
    mff101.flip_time_ms = 1000.0
    assert mff101.flip_time_ms == 1000.0

def test_invalid_flip_time(mff101):
    # test lower bound
    mff101.flip_time_ms = FLIP_TIME_RANGE[0] - 0.1
    assert mff101.flip_time_ms == FLIP_TIME_RANGE[0]
    # test upper bound
    mff101.flip_time_ms = FLIP_TIME_RANGE[1] + 1
    assert mff101.flip_time_ms == FLIP_TIME_RANGE[1]

def test_different_switch_times(mff101):
    mff101.position = 'A'
    mff101.wait()

    cycles = 5
    switch_times = [500, 1000, 1500, 2000, 2800]
    for switch_time in switch_times:
        mff101.flip_time_ms = switch_time
        for _ in range(cycles):

            time.sleep(1)
            mff101.toggle(wait=True)
            assert mff101.position == 'B'

            time.sleep(1)
            mff101.toggle(wait=True)
            assert mff101.position == 'A'

def test_reset(mff101):
    mff101.flip_time_ms = 500
    mff101.position = 'B'
    mff101.wait()
    assert mff101.position == 'B'
    assert mff101.flip_time_ms == 500

    mff101.reset()
    mff101.wait()
    assert mff101.position == 'A'
    assert mff101.flip_time_ms == 1000
