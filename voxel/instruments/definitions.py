from typing import Dict

from voxel.devices import VoxelDeviceType

ChannelsDict = Dict[str, Dict[str, str]]

CHANNEL_DEVICES = [VoxelDeviceType.CAMERA, VoxelDeviceType.LASER, VoxelDeviceType.FILTER]
