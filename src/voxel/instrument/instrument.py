from typing import Dict, Optional, Tuple

from voxel.instrument._config import InstrumentConfig
from voxel.instrument._definitions import VoxelDeviceType
from voxel.instrument.channel import VoxelChannel
from voxel.instrument.device import VoxelDevice
from voxel.instrument.devices.camera import VoxelCamera
from voxel.instrument.devices.filter import VoxelFilter
from voxel.instrument.devices.laser import VoxelLaser
from voxel.instrument.devices.lens import VoxelLens
from voxel.instrument.devices.linear_axis import LinearAxisDimension
from voxel.instrument.devices.linear_axis import VoxelLinearAxis
from voxel.instrument.file_transfers.base import VoxelFileTransfer
from voxel.instrument.nidaq import VoxelNIDAQ
from voxel.instrument.writers import VoxelWriter
from voxel.utils.geometry.vec import Vec3D
from voxel.utils.logging import get_logger


class VoxelStage:
    def __init__(self, x: VoxelLinearAxis, y: VoxelLinearAxis, z: Optional[VoxelLinearAxis] = None):
        self.x = x
        self.y = y
        self.z = z

    @property
    def position_mm(self) -> Vec3D:
        return Vec3D(self.x.position_mm, self.y.position_mm, self.z.position_mm or 0)

    @property
    def limits_mm(self) -> Tuple[Vec3D, Vec3D]:
        return Vec3D(self.x.lower_limit_mm, self.y.lower_limit_mm, self.z.lower_limit_mm or 0), \
            Vec3D(self.x.upper_limit_mm, self.y.upper_limit_mm, self.z.upper_limit_mm or 0)


class VoxelInstrument:

    def __init__(self,
                 devices: Dict[str, VoxelDevice],
                 channels: Optional[Dict[str, VoxelChannel]] = None,
                 writers: Optional[Dict[str, VoxelWriter]] = None,
                 file_transfers: Optional[Dict[str, VoxelFileTransfer]] = None,
                 name: Optional[str] = None,
                 config: Optional[InstrumentConfig] = None,
                 daq: Optional[VoxelNIDAQ] = None,
                 **kwds
                 ):
        self.log = get_logger(self.__class__.__name__)
        self.name = name
        self.config = config
        self.devices = devices
        self.writers = writers
        self.file_transfers = file_transfers
        self.channels = channels
        self.daq = daq
        self.kwds = kwds
        self.validate_device_names()
        self.active_devices = {device_name: False for device_name in self.devices.keys()}
        self.stage = self._create_stage()
        self.apply_build_settings()

    def __repr__(self):
        devices_str = '\n\t - '.join([f"{device}" for device in self.devices.values()])
        return (
            f"{self.__class__.__name__} "
            f"Devices: \n\t - "
            f"{devices_str} \n"
        )

    def activate_channel(self, channel_name: str):
        if not self.channels:
            return
        channel = self.channels[channel_name]
        for device_name in channel.devices.keys():
            if self.active_devices[device_name]:
                self.log.error(f"Unable to activate channel {channel_name}. "
                               f"Device {device_name} is possibly in use by another channel.")
                return
        channel.activate()
        self.active_devices.update({device_name: True for device_name in channel.devices.keys()})

    def deactivate_channel(self, channel_name: str):
        if not self.channels:
            return
        channel = self.channels[channel_name]
        channel.deactivate()
        self.active_devices.update({device_name: False for device_name in channel.devices.keys()})

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

    def apply_build_settings(self):
        if self.config:
            settings = self.config.settings
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

    def _create_stage(self) -> VoxelStage:
        axes = {LinearAxisDimension.X: None, LinearAxisDimension.Y: None, LinearAxisDimension.Z: None}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.LINEAR_AXIS:
                assert isinstance(device, VoxelLinearAxis), f"Device {name} is not a VoxelLinearAxis"
                if not axes[device.dimension]:
                    axes[device.dimension] = device
        return VoxelStage(axes[LinearAxisDimension.X], axes[LinearAxisDimension.Y], axes[LinearAxisDimension.Z])

    def close(self):
        for device in self.devices.values():
            device.close()
        self.daq.close()
