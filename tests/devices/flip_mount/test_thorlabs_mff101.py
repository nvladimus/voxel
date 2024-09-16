import time
import os

import pytest

from voxel.instrument.devices.flip_mount.thorlabs_mff101 import ThorlabsFlipMount, FLIP_TIME_RANGE_MS
from tests.devices.conftest import thorlabs_mff101, POSITION_1, POSITION_2, WRONG_POSITION

POSITION_1 = 'A'
POSITION_2 = 'B'


def test_connect(thorlabs_mff101):
    assert thorlabs_mff101._inst is not None
    thorlabs_mff101.wait()
    assert thorlabs_mff101.position == POSITION_1


def test_close(thorlabs_mff101):
    thorlabs_mff101.close()
    assert thorlabs_mff101._inst is None


def test_position(thorlabs_mff101):
    thorlabs_mff101.wait()
    assert thorlabs_mff101.position == POSITION_1

    thorlabs_mff101.position = POSITION_2
    thorlabs_mff101.wait()
    assert thorlabs_mff101.position == POSITION_2

    thorlabs_mff101.position = POSITION_1
    thorlabs_mff101.wait()
    assert thorlabs_mff101.position == POSITION_2


def test_toggle(thorlabs_mff101):
    thorlabs_mff101.wait()
    assert thorlabs_mff101.position == POSITION_1

    thorlabs_mff101.toggle(wait=True)
    assert thorlabs_mff101.position == POSITION_2

    thorlabs_mff101.toggle(wait=True)
    assert thorlabs_mff101.position == POSITION_1


def test_invalid_position(thorlabs_mff101):
    with pytest.raises(ValueError):
        thorlabs_mff101.position = WRONG_POSITION


def test_flip_time_ms(thorlabs_mff101):
    assert thorlabs_mff101.flip_time_ms == 1000.0  # default switch time
    thorlabs_mff101.flip_time_ms = 500.0
    assert thorlabs_mff101.flip_time_ms == 500.0
    thorlabs_mff101.flip_time_ms = 1000.0
    assert thorlabs_mff101.flip_time_ms == 1000.0


def test_invalid_flip_time(thorlabs_mff101):
    # test lower bound
    thorlabs_mff101.flip_time_ms = FLIP_TIME_RANGE_MS[0] - 0.1
    assert thorlabs_mff101.flip_time_ms == FLIP_TIME_RANGE_MS[0]
    # test upper bound
    thorlabs_mff101.flip_time_ms = FLIP_TIME_RANGE_MS[1] + 1
    assert thorlabs_mff101.flip_time_ms == FLIP_TIME_RANGE_MS[1]


def test_different_switch_times(thorlabs_mff101):
    thorlabs_mff101.position = POSITION_1
    thorlabs_mff101.wait()

    cycles = 5
    switch_times = [500, 1000, 1500, 2000, 2800]
    for switch_time in switch_times:
        thorlabs_mff101.flip_time_ms = switch_time
        for _ in range(cycles):
            time.sleep(1)
            thorlabs_mff101.toggle(wait=True)
            assert thorlabs_mff101.position == POSITION_2

            time.sleep(1)
            thorlabs_mff101.toggle(wait=True)
            assert thorlabs_mff101.position == POSITION_1
