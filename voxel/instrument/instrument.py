import logging
from typing import Dict, Any

from voxel.instrument.config import InstrumentConfig
from voxel.instrument.definitions import VoxelDeviceType, ChannelsDict
from voxel.instrument.device import VoxelDevice
from voxel.instrument.devices.camera import VoxelCamera
from voxel.instrument.devices.filter import VoxelFilter
from voxel.instrument.devices.laser import VoxelLaser
from voxel.instrument.devices.linear_axis import VoxelLinearAxis
from voxel.instrument.nidaq import VoxelNIDAQ


class VoxelInstrument:

    def __init__(self, name: str, config: InstrumentConfig, devices: Dict[str, VoxelDevice], daq: VoxelNIDAQ,
                 channels: ChannelsDict, **kwds):
        self.name = name
        self.config = config
        self.devices = devices
        self.daq = daq
        self.channels = channels
        self.kwds = kwds
        self.log = logging.getLogger(self.__class__.__name__)
        self.apply_build_settings()
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

    def apply_build_settings(self):
        self._apply_settings(self.config.startup_settings())

    def close(self):
        for device in self.devices.values():
            device.close()
        self.daq.close()

    def _apply_settings(self, settings: Dict[str, Dict[str, Any]]):
        if settings:
            for name, device_settings in settings.items():
                instance = self.devices[name] or self.daq.tasks[name]
                if instance:
                    self._apply_instance_settings(instance, device_settings)

    def _apply_instance_settings(self, device: VoxelDevice, settings: Dict[str, Any]):
        for key, value in settings.items():
            try:
                setattr(device, key, value)
            except AttributeError:
                self.log.error(f"Instance '{device.name}' has no attribute '{key}'")
            except Exception as e:
                self.log.error(f"Error setting '{key}' for '{device.name}': {str(e)}")
                raise
        self.log.info(f"Applied settings to '{device.name}'")
