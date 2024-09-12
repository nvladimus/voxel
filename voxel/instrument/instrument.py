from typing import Dict, Optional

from instrument.channel import VoxelChannel
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
                 channels: Optional[Dict[str, VoxelChannel]] = None,
                 **kwds
                 ):
        self.name = name
        self.config = config
        self.devices = devices
        self.daq = daq
        self.channels = channels
        self.kwds = kwds
        self.log = get_logger(self.__class__.__name__)
        self.active_devices = {device_name: False for device_name in self.devices.keys()}
        self.apply_build_settings()
        if self.channels:
            self.activate_channel(list(self.channels.keys())[0])

    def __repr__(self):
        devices_str = '\n\t - '.join([f"{device}" for device in self.devices.values()])
        return (
            f"{self.__class__.__name__} "
            f"Devices: \n\t - "
            f"{devices_str} \n"
            f"Channels: \n{self.channels}"
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
    def stage_axes(self) -> Dict[str, VoxelLinearAxis]:
        stage_axes = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.LINEAR_AXIS:
                assert isinstance(device, VoxelLinearAxis), f"Device {name} is not a VoxelLinearAxis"
                stage_axes[name] = device
        return stage_axes

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

    def apply_build_settings(self):
        if self.config:
            settings = self.config.startup_settings()
            if settings:
                for name, device_settings in settings.items():
                    instance = self.devices[name]
                    if instance:
                        instance.apply_settings(device_settings)

    def close(self):
        for device in self.devices.values():
            device.close()
        self.daq.close()
