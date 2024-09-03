import logging
from typing import Dict

from voxel.devices import VoxelDevice
from voxel.devices.definitions import VoxelDeviceType
from voxel.instruments.config import InstrumentConfig

ChannelsDict = Dict[str, Dict[str, str]]


class VoxelInstrument:

    def __init__(self, config: InstrumentConfig, devices: Dict[str, VoxelDevice], channels: ChannelsDict, **kwds):
        self.config = config
        self.devices = devices
        self.channels = channels
        self.kwds = kwds
        self.log = logging.getLogger(self.__class__.__name__)

    def __repr__(self):
        devices_str = '\n\t - '.join([f"{device}" for device in self.devices.values()])
        return (
            f"{self.__class__.__name__} "
            f"Devices: \n\t - "
            f"{devices_str} \n"
            f"Channels: \n{self.channels}"
        )

    @property
    def cameras(self):
        cameras = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.CAMERA:
                cameras[name] = device
        return cameras

    @property
    def lasers(self):
        lasers = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.LASER:
                lasers[name] = device
        return lasers

    @property
    def stage_axes(self):
        stage_axes = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.LINEAR_AXIS:
                stage_axes[name] = device
        return stage_axes

    def close(self):
        for device in self.devices.values():
            device.close()
