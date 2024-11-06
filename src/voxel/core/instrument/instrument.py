from voxel.core.instrument.channel import VoxelChannel
from voxel.core.instrument.daq import VoxelDaq
from voxel.core.instrument.device import VoxelDevice, VoxelDeviceType
from voxel.core.instrument.device.camera import VoxelCamera
from voxel.core.instrument.device.filter import VoxelFilter, VoxelFilterWheel
from voxel.core.instrument.device.laser import VoxelLaser
from voxel.core.instrument.device.lens import VoxelLens
from voxel.core.instrument.device.linear_axis import LinearAxisDimension, VoxelLinearAxis
from voxel.core.instrument.device.transfer import VoxelFileTransfer
from voxel.core.instrument.device.writer import VoxelWriter
from voxel.core.instrument.stage import VoxelStage
from voxel.core.utils.log_config import get_component_logger


class VoxelInstrument:

    def __init__(
        self,
        devices: dict[str, VoxelDevice],
        channels: dict[str, VoxelChannel] | None = None,
        writers: dict[str, VoxelWriter] | None = None,
        file_transfers: dict[str, VoxelFileTransfer] | None = None,
        name: str = "Instrument",
        build_settings=None,
        daq: VoxelDaq | None = None,
    ) -> None:
        self.name = name
        self.log = get_component_logger(self)
        self.build_settings = build_settings
        self.devices = devices
        self.writers = writers
        self.file_transfers = file_transfers
        self.channels = channels
        self.daq = daq
        self.validate_device_names()
        self.active_devices = {device_name: False for device_name in self.devices.keys()}
        self.stage = self._create_stage()
        self.apply_build_settings()

    def __repr__(self) -> str:
        devices_str = "\n\t - ".join([f"{device}" for device in self.devices.values()])
        return f"{self.__class__.__name__} " f"Devices: \n\t - " f"{devices_str} \n"

    def activate_channel(self, channel_name: str) -> None:
        if not self.channels:
            return
        channel = self.channels[channel_name]
        for device_name in channel.devices.keys():
            if self.active_devices[device_name]:
                self.log.error(
                    f"Unable to activate channel {channel_name}. "
                    f"Device {device_name} is possibly in use by another channel."
                )
                return
        channel.activate()
        self.active_devices.update({device_name: True for device_name in channel.devices.keys()})

    def deactivate_channel(self, channel_name: str) -> None:
        if not self.channels:
            return
        channel = self.channels[channel_name]
        channel.deactivate()
        self.active_devices.update({device_name: False for device_name in channel.devices.keys()})

    @property
    def cameras(self) -> dict[str, VoxelCamera]:
        cameras = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.CAMERA:
                assert isinstance(device, VoxelCamera), f"Device {name} is not a VoxelCamera"
                cameras[name] = device
        return cameras

    @property
    def lenses(self) -> dict[str, VoxelLens]:
        lenses = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.LENS:
                assert isinstance(device, VoxelLens), f"Device {name} is not a VoxelLens"
                lenses[name] = device
        return lenses

    @property
    def lasers(self) -> dict[str, VoxelLaser]:
        lasers = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.LASER:
                assert isinstance(device, VoxelLaser), f"Device {name} is not a VoxelLaser"
                lasers[name] = device
        return lasers

    @property
    def filters(self) -> dict[str, VoxelFilter]:
        filters = {}
        for name, device in self.devices.items():
            if device.device_type == VoxelDeviceType.FILTER:
                assert isinstance(device, VoxelFilter), f"Device {name} is not a VoxelFilter"
                filters[name] = device
        return filters

    def apply_build_settings(self):
        if self.build_settings:
            for name, device_settings in self.build_settings.items():
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
        self.daq.clean_up()


__all__ = [
    "VoxelInstrument",
    "VoxelChannel",
    "VoxelDevice",
    "VoxelDeviceType",
    "VoxelCamera",
    "VoxelLens",
    "VoxelLaser",
    "VoxelFilterWheel",
    "VoxelLinearAxis",
    "LinearAxisDimension",
    "VoxelStage",
    "VoxelWriter",
    "VoxelFileTransfer",
]
