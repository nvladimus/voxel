from dataclasses import dataclass

from voxel.instrument.definitions import VoxelDeviceType
from voxel.instrument.devices.camera import VoxelCamera
from voxel.instrument.devices.filter import VoxelFilter
from voxel.instrument.devices.laser import VoxelLaser
from voxel.instrument.devices.lens import VoxelLens

CHANNEL_DEVICES = [VoxelDeviceType.CAMERA, VoxelDeviceType.LASER, VoxelDeviceType.FILTER]


@dataclass
class VoxelChannel:
    """A channel in a voxel instrument."""
    name: str
    camera: VoxelCamera
    lens: VoxelLens
    laser: VoxelLaser
    emmision_filter: VoxelFilter
    is_active: bool = False

    def __post_init__(self):
        self._fov_um = self.camera.sensor_size_um / self.lens.magnification
        self.devices = {device.name: device for device in [self.camera, self.lens, self.laser, self.emmision_filter]}

    @property
    def fov_um(self):
        return self._fov_um

    def apply_settings(self, settings: dict):
        """Apply settings to the channel."""
        if not settings:
            return
        if 'camera' in settings:
            self.camera.apply_settings(settings['camera'])
        if 'lens' in settings:
            self.lens.apply_settings(settings['lens'])
        if 'laser' in settings:
            self.laser.apply_settings(settings['laser'])
        if 'filter' in settings:
            self.emmision_filter.apply_settings(settings['filter'])

    def activate(self):
        """Activate the channel."""
        for device in [self.laser, self.emmision_filter]:
            device.enable()
        self.is_active = True

    def deactivate(self):
        """Deactivate the channel."""
        for device in [self.laser, self.emmision_filter]:
            device.disable()
        self.is_active = False
