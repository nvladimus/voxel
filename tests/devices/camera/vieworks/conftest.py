from unittest.mock import patch, MagicMock

import pytest

from voxel.devices.camera.vieworks import VieworksCamera

CAMERA_1_SN = 'MP151BBX006'
CAMERA_2_SN = 'MB151BAY001'

@pytest.fixture
def mock_camera():
    with (
        # patch('voxel.devices.camera.vieworks.egrabber.EGrabber') as mock_egrabber,
        # patch('voxel.devices.camera.vieworks.vieworks_egrabber.EGenTLSingleton') as mock_gentl,
        patch('voxel.devices.camera.vieworks.vieworks_egrabber._discover_grabber') as mock_discover
    ):
        mock_grabber = MagicMock()
        mock_egrabber_dict = {
            "interface": 0,
            "device": 0,
            "stream": 0
        }
        mock_discover.return_value = (mock_grabber, mock_egrabber_dict)
        camera = VieworksCamera(id='mock_camera', serial_number='12345')
        camera.grabber = mock_grabber
        yield camera


@pytest.fixture(scope="module")
def real_camera():
    camera = VieworksCamera(id='real_camera', serial_number=CAMERA_1_SN)
    yield camera
    camera.close()
