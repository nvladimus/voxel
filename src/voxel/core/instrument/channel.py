from dataclasses import dataclass
from typing import Any

from voxel.core.instrument.device.camera import VoxelCamera
from voxel.core.instrument.device.filter import VoxelFilter
from voxel.core.instrument.device.laser import VoxelLaser
from voxel.core.instrument.device.lens import VoxelLens
from voxel.core.instrument.io.transfer import VoxelFileTransfer
from voxel.core.instrument.io.writer import VoxelWriter
from voxel.core.utils.geometry.vec import Vec2D


@dataclass
class VoxelChannel:
    """A channel in a voxel instrument."""

    name: str
    camera: VoxelCamera
    lens: VoxelLens
    laser: VoxelLaser
    emmision_filter: VoxelFilter
    is_active: bool = False
    writer: VoxelWriter = None
    file_transfer: VoxelFileTransfer = None

    def __post_init__(self) -> None:
        self._fov_um = self.camera.sensor_size_um / self.lens.magnification
        self.devices = {device.name: device for device in [self.camera, self.lens, self.laser, self.emmision_filter]}

    @property
    def fov_um(self) -> Vec2D:
        return self._fov_um

    def apply_settings(self, settings: dict[str, dict[str, Any]]) -> None:
        """Apply settings to the channel."""
        if not settings:
            return
        if "camera" in settings:
            self.camera.apply_settings(settings["camera"])
        if "lens" in settings:
            self.lens.apply_settings(settings["lens"])
        if "laser" in settings:
            self.laser.apply_settings(settings["laser"])
        if "filter" in settings:
            self.emmision_filter.apply_settings(settings["filter"])

    def activate(self) -> None:
        """Activate the channel."""
        for device in [self.laser, self.emmision_filter]:
            device.enable()
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate the channel."""
        for device in [self.laser, self.emmision_filter]:
            device.disable()
        self.is_active = False
