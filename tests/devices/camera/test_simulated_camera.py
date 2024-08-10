import pytest
from voxel.devices.camera.simulated import (
    SimulatedCamera,
    BUFFER_SIZE_FRAMES,
    MIN_WIDTH_PX,
    MAX_WIDTH_PX,
    STEP_WIDTH_PX,
    MIN_HEIGHT_PX,
    MAX_HEIGHT_PX,
    STEP_HEIGHT_PX,
    MIN_EXPOSURE_TIME_MS,
    MAX_EXPOSURE_TIME_MS,
    STEP_EXPOSURE_TIME_MS,
    BINNING,
    PIXEL_TYPES,
    LINE_INTERVALS_US,
    TRIGGERS,
)

CAMERA_ID = "camera-1"
CAMERA_SN = "1234567890"
INIT_EXPOSURE_TIME_MS = 10.0


@pytest.fixture
def simulated_camera():
    camera = SimulatedCamera(id=CAMERA_ID, serial_number=CAMERA_SN)
    yield camera
    camera.close()


def test_camera_init(simulated_camera):
    assert simulated_camera.id == CAMERA_ID
    assert simulated_camera.serial_number == CAMERA_SN
    assert simulated_camera.roi_width_offset_px == 0
    assert simulated_camera.roi_height_offset_px == 0
    assert simulated_camera.exposure_time_ms == INIT_EXPOSURE_TIME_MS


""" Test Image Size Properties ______________________________________________________________________________________"""


def test_roi_width_px(simulated_camera):
    def _calculate_width_offset(width_px):
        return round((MAX_WIDTH_PX  // 2 - width_px // 2) / STEP_WIDTH_PX) * STEP_WIDTH_PX

    assert simulated_camera.roi_width_px == MAX_WIDTH_PX
    assert simulated_camera.roi_width_offset_px == 0

    simulated_camera.roi_width_px = 1024
    assert simulated_camera.roi_width_px == 1024
    assert simulated_camera.roi_width_offset_px == _calculate_width_offset(1024)

    simulated_camera.roi_width_px = 4096
    assert simulated_camera.roi_width_px == 4096
    assert simulated_camera.roi_width_offset_px == _calculate_width_offset(4096)

    simulated_camera.roi_width_px = MIN_WIDTH_PX - 1.0
    assert simulated_camera.roi_width_px == MIN_WIDTH_PX
    assert simulated_camera.roi_width_offset_px == _calculate_width_offset(MIN_WIDTH_PX)

    simulated_camera.roi_width_px = MAX_WIDTH_PX + 1.0
    assert simulated_camera.roi_width_px == MAX_WIDTH_PX
    assert simulated_camera.roi_width_offset_px == 0


def test_roi_height_px(simulated_camera):
    def _calculate_height_offset(height_px):
        return round((MAX_HEIGHT_PX  // 2 - height_px // 2) / STEP_HEIGHT_PX) * STEP_HEIGHT_PX

    assert simulated_camera.roi_height_px == MAX_HEIGHT_PX
    assert simulated_camera.roi_height_offset_px == 0

    simulated_camera.roi_height_px = 1024
    assert simulated_camera.roi_height_px == 1024
    assert simulated_camera.roi_height_offset_px == _calculate_height_offset(1024)

    simulated_camera.roi_height_px = 4096
    assert simulated_camera.roi_height_px == 4096
    assert simulated_camera.roi_height_offset_px == _calculate_height_offset(4096)

    simulated_camera.roi_height_px = MIN_HEIGHT_PX - 1.0
    assert simulated_camera.roi_height_px == MIN_HEIGHT_PX
    assert simulated_camera.roi_height_offset_px == _calculate_height_offset(MIN_HEIGHT_PX)

    simulated_camera.roi_height_px = MAX_HEIGHT_PX + 1.0
    assert simulated_camera.roi_height_px == MAX_HEIGHT_PX
    assert simulated_camera.roi_height_offset_px == 0


def test_binning(simulated_camera):
    assert simulated_camera.binning == BINNING[1]
    assert simulated_camera.image_width_px == simulated_camera.roi_width_px
    assert simulated_camera.image_height_px == simulated_camera.roi_height_px

    simulated_camera.binning = BINNING[2]
    assert simulated_camera.binning == BINNING[2]
    assert simulated_camera.image_width_px == simulated_camera.roi_width_px // 2
    assert simulated_camera.image_height_px == simulated_camera.roi_height_px // 2

    simulated_camera.binning = BINNING[4]
    assert simulated_camera.binning == BINNING[4]
    assert simulated_camera.image_width_px == simulated_camera.roi_width_px // 4
    assert simulated_camera.image_height_px == simulated_camera.roi_height_px // 4

    with pytest.raises(ValueError):
        simulated_camera.binning = 3

    with pytest.raises(ValueError):
        simulated_camera.binning = 5


""" Test Image Format Properties ____________________________________________________________________________________"""


def test_pixel_type(simulated_camera):
    assert simulated_camera.pixel_type == "mono16"

    simulated_camera.pixel_type = "mono8"
    assert simulated_camera.pixel_type == "mono8"

    simulated_camera.pixel_type = "mono16"
    assert simulated_camera.pixel_type == "mono16"

    with pytest.raises(ValueError):
        simulated_camera.pixel_type = "rgb"



"""

def test_trigger(simulated_camera):
    assert simulated_camera.trigger == {
        "mode": "on",
        "source": "internal",
        "polarity": "rising",
    }

    simulated_camera.trigger = {
        "mode": "off",
        "source": "line0",
        "polarity": "fallingedge",
    }
    assert simulated_camera.trigger == {
        "mode": "off",
        "source": "line0",
        "polarity": "fallingedge",
    }

    with pytest.raises(ValueError):
        simulated_camera.trigger = {
            "mode": "invalid",
            "source": "line0",
            "polarity": "rising",
        }

    with pytest.raises(ValueError):
        simulated_camera.trigger = {
            "mode": "on",
            "source": "invalid",
            "polarity": "rising",
        }

    with pytest.raises(ValueError):
        simulated_camera.trigger = {
            "mode": "on",
            "source": "line0",
            "polarity": "invalid",
        }


def test_sensor_width_px(simulated_camera):
    assert simulated_camera.sensor_width_px == 2048


def test_sensor_height_px(simulated_camera):
    assert simulated_camera.sensor_height_px == 2048


def test_grab_frame(simulated_camera):
    frame = simulated_camera.grab_frame()
    assert frame.shape == (2048, 2048)


def test_signal_acquisition_state(simulated_camera):
    state = simulated_camera.acquisition_state()
    assert "Frame Index" in state
    assert "Input Buffer Size" in state
    assert "Output Buffer Size" in state
    assert "Dropped Frames" in state
    assert "Data Rate [MB/s]" in state
    assert "Frame Rate [fps]" in state


def test_log_metadata(simulated_camera):
    simulated_camera.log_metadata()
    # Assert that the function does not raise any errors
"""


def test_exposure_time(simulated_camera):
    assert simulated_camera.exposure_time_ms == INIT_EXPOSURE_TIME_MS

    simulated_camera.exposure_time_ms = 20.0
    assert simulated_camera.exposure_time_ms == 20.0

    simulated_camera.exposure_time_ms = 5.0
    assert simulated_camera.exposure_time_ms == 5.0

    simulated_camera.exposure_time_ms = MIN_EXPOSURE_TIME_MS - 1.0
    assert simulated_camera.exposure_time_ms == MIN_EXPOSURE_TIME_MS

    simulated_camera.exposure_time_ms = MAX_EXPOSURE_TIME_MS + 1.0
    assert simulated_camera.exposure_time_ms == MAX_EXPOSURE_TIME_MS

