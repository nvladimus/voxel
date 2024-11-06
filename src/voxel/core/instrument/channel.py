from typing import Any

from voxel.core.acquisition.model.frame_stack import FrameStack
from voxel.core.utils.geometry.vec import Vec2D, Vec3D
from voxel.core.utils.log_config import get_component_logger

from .device.camera import VoxelCamera
from .device.filter import VoxelFilter
from .device.laser import VoxelLaser
from .device.lens import VoxelLens
from .device.transfer import VoxelFileTransfer
from .device.writer import VoxelWriter, WriterMetadata


class VoxelChannel:
    """A channel in a voxel instrument."""

    def __init__(
        self,
        name: str,
        camera: VoxelCamera,
        lens: VoxelLens,
        laser: VoxelLaser,
        emmision_filter: VoxelFilter,
        is_active: bool = False,
        writer: VoxelWriter = None,
        file_transfer: VoxelFileTransfer = None,
    ) -> None:
        self.name = name
        self.log = get_component_logger(self)
        self.camera = camera
        self.lens = lens
        self.laser = laser
        self.emmision_filter = emmision_filter
        self.is_active = is_active
        self.writer = writer
        self.file_transfer = file_transfer
        self._fov_um = self.camera.sensor_size_um / self.lens.magnification
        self.devices = {device.name: device for device in [self.camera, self.lens, self.laser, self.emmision_filter]}

    @property
    def fov_um(self) -> Vec2D:
        return self._fov_um

    def configure_writer(self, stack: FrameStack, channel_idx: int) -> None:
        """Configure the writer for the channel."""
        if not self.writer:
            raise RuntimeError("No writer to configure.")
        self.writer.configure(
            WriterMetadata(
                frame_count=stack.frame_count,
                frame_shape=self.camera.frame_size_px,
                position=stack.pos,
                channel_name=self.name,
                channel_idx=channel_idx,
                voxel_size=Vec3D(self.camera.pixel_size_um.x, self.camera.pixel_size_um.y, stack.z_step_size),
                file_name=f"{stack.idx.x}_{stack.idx.y}_{self.name}",
            )
        )

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
