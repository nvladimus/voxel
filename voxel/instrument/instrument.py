from typing import Dict, Optional, Tuple

from voxel.instrument.devices.lens import VoxelLens
from voxel.instrument.devices.linear_axis import LinearAxisDimension
from voxel.utils.geometry.vec import Vec3D
from voxel.instrument.config import InstrumentConfig
from voxel.instrument.definitions import VoxelDeviceType
from voxel.instrument.device import VoxelDevice
from voxel.instrument.devices.camera import VoxelCamera
from voxel.instrument.devices.filter import VoxelFilter
from voxel.instrument.devices.laser import VoxelLaser
from voxel.instrument.devices.linear_axis import VoxelLinearAxis
from voxel.instrument.nidaq import VoxelNIDAQ
from voxel.utils.logging import get_logger


class VoxelInstrument:

    def __init__(self,
                 devices: Dict[str, VoxelDevice],
                 name: Optional[str] = None,
                 config: Optional[InstrumentConfig] = None,
                 daq: Optional[VoxelNIDAQ] = None,
                 **kwds
                 ):
        self.name = name
        self.config = config
        self.devices = devices
        self.daq = daq
        self.kwds = kwds
        self.log = get_logger(self.__class__.__name__)
        self.validate_device_names()
        if self.stage_axes:
            try:
                self.x_axis = self.stage_axes[LinearAxisDimension.X]
                self.y_axis = self.stage_axes[LinearAxisDimension.Y]
                self.z_axis = self.stage_axes[LinearAxisDimension.Z]
            except KeyError as e:
                self.log.error(f"Missing stage axis: {e}")
        self.apply_build_settings()

    def __repr__(self):
        devices_str = '\n\t - '.join([f"{device}" for device in self.devices.values()])
        return (
            f"{self.__class__.__name__} "
            f"Devices: \n\t - "
            f"{devices_str} \n"
        )

    @property
    def cameras(self) -> Dict[str, VoxelCamera]:
        cameras = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.CAMERA:
                assert isinstance(device, VoxelCamera), f"Device {name} is not a VoxelCamera"
                cameras[name] = device
        return cameras

    @property
    def lenses(self) -> Dict[str, VoxelLens]:
        lenses = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.LENS:
                assert isinstance(device, VoxelLens), f"Device {name} is not a VoxelLens"
                lenses[name] = device
        return lenses

    @property
    def lasers(self) -> Dict[str, VoxelLaser]:
        lasers = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.LASER:
                assert isinstance(device, VoxelLaser), f"Device {name} is not a VoxelLaser"
                lasers[name] = device
        return lasers

    @property
    def filters(self) -> Dict[str, VoxelFilter]:
        filters = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.FILTER:
                assert isinstance(device, VoxelFilter), f"Device {name} is not a VoxelFilter"
                filters[name] = device
        return filters

    @property
    def stage_axes(self) -> Dict[LinearAxisDimension, VoxelLinearAxis]:
        stage_axes = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.LINEAR_AXIS:
                assert isinstance(device, VoxelLinearAxis), f"Device {name} is not a VoxelLinearAxis"
                stage_axes[device.dimension] = device
        return stage_axes

    @property
    def stage_position_mm(self) -> Vec3D:
        """Return the current position of the stage in mm"""
        return Vec3D(self.x_axis.position_mm, self.y_axis.position_mm, self.z_axis.position_mm)

    @property
    def stage_limits_mm(self) -> Tuple[Vec3D, Vec3D]:
        """Return the limits of the stage in mm"""
        return Vec3D(self.x_axis.lower_limit_mm, self.y_axis.lower_limit_mm, self.z_axis.lower_limit_mm), \
            Vec3D(self.x_axis.upper_limit_mm, self.y_axis.upper_limit_mm, self.z_axis.upper_limit_mm)

    def apply_build_settings(self):
        if self.config:
            settings = self.config.startup_settings()
            if settings:
                for name, device_settings in settings.items():
                    instance = self.devices[name]
                    if instance:
                        instance.apply_settings(device_settings)

    def validate_device_names(self):
        for key, device in self.devices.items():
            if device.name != key:
                device.name = key
                self.log.warning(f"Device name mismatch. Setting device name to {key}")

    def close(self):
        for device in self.devices.values():
            device.close()
        self.daq.close()
