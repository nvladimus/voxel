import pytest
from unittest.mock import patch, MagicMock
from voxel.devices.camera.vieworks import VieworksCamera

VIEWORKS_CAMERA_ID = 'test_vieworks_camera'
VIEWORKS_SERIAL_NUMBER = 'MP151BBX006'

CAMERA_1_sn = 'MB151BAY001'
CAMERA_2_SN = 'MP151BBX006'

@pytest.fixture
def mock_camera():
    with (
        # patch('voxel.devices.camera.vieworks.egrabber.EGrabber') as mock_egrabber,
        # patch('voxel.devices.camera.vieworks.vieworks_egrabber.EGenTLSingleton') as mock_gentl,
        patch('voxel.devices.camera.vieworks.vieworks_egrabber.VieworksCamera._discover_camera') as mock_discover
    ):
        mock_grabber = MagicMock()
        mock_egrabber_dict = {
            "interface": 0,
            "device": 0,
            "stream": 0
        }
        mock_discover.return_value = (mock_grabber, mock_egrabber_dict)
        camera = VieworksCamera(id=VIEWORKS_CAMERA_ID, serial_number=VIEWORKS_SERIAL_NUMBER)
        camera.grabber = mock_grabber
        yield camera


@pytest.fixture(scope="module")
def real_camera():
    camera = VieworksCamera(id=VIEWORKS_CAMERA_ID, serial_number=VIEWORKS_SERIAL_NUMBER)
    yield camera
    camera.close()
