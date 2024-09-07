import logging
from typing import Dict

from voxel.devices import VoxelDevice, VoxelCamera, VoxelLaser, VoxelLinearAxis, VoxelFilter
from voxel.devices.definitions import VoxelDeviceType
from voxel.instruments.config import InstrumentConfig
from voxel.instruments.definitions import ChannelsDict


class VoxelInstrument:

    def __init__(self, config: InstrumentConfig, devices: Dict[str, VoxelDevice], daq: VoxelDeviceType,
                 channels: ChannelsDict, **kwds):
        self.config = config
        self.devices = devices
        self.daq = daq
        self.channels = channels
        self.kwds = kwds
        self.log = logging.getLogger(self.__class__.__name__)
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
        channel = self.channels[channel_name]
        for device_type, device_name in channel.items():
            device = self.devices[device_name]
            match device.device_type:
                case VoxelDeviceType.LASER:
                    assert isinstance(device, VoxelLaser), f"Device {device_name} is not a VoxelLaser"
                    device.enable()
                case VoxelDeviceType.FILTER:
                    assert isinstance(device, VoxelFilter), f"Device {device_name} is not a VoxelFilter"
                    device.enable()
                case _:
                    pass

    def close(self):
        for device in self.devices.values():
            device.close()
