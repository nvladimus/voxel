from typing import Optional, Dict

from voxel.acquisition.channel import VoxelChannel
from voxel import VoxelInstrument
from voxel.acquisition.config import AcquisitionConfig
from voxel.acquisition.file_transfers.base import VoxelFileTransfer
from voxel.acquisition.metadata.base import VoxelMetadata
from voxel.acquisition.volume import Volume
from voxel.acquisition.writers import VoxelWriter
from voxel.utils.logging import get_logger


class VoxelAcquisition:

    def __init__(self, config: AcquisitionConfig, instrument: VoxelInstrument, metadata_handler: VoxelMetadata,
                 writers: Dict[str, VoxelWriter], file_transfers: Dict[str, VoxelFileTransfer],
                 name: Optional[str] = None):
        self.log = get_logger(f"{self.__class__.__name__}")
        self.name = name
        self.config = config
        self.instrument = instrument
        self.metadata = metadata_handler
        self.writers = writers
        self.file_transfers = file_transfers
        self.channels = self._construct_channels()
        self.active_devices = {device_name: False for device_name in self.instrument.devices.keys()}
        self.volume = Volume(
            tile_name_prefix=f"{self.name}",
            step_size=self.config.acquisition_specs["step_size"],
            tile_overlap=0.15,
            stage_limits_mm=self.instrument.stage_limits_mm
        )
        self.log.debug(f"Acquisition created with instrument: {instrument}")

    def _construct_channels(self) -> Dict[str, VoxelChannel]:
        channels = {}
        for channel_name, channel_specs in self.config.channel_specs.items():
            channels[channel_name] = VoxelChannel(
                name=channel_name,
                camera=self.instrument.cameras[channel_specs["camera"]],
                lens=self.instrument.lenses[channel_specs["lens"]],
                laser=self.instrument.lasers[channel_specs["laser"]],
                emmision_filter=self.instrument.filters[channel_specs["filter"]],
                writer=self.writers[channel_specs["writer"]],
                file_transfer=self.file_transfers[channel_specs["file_transfer"]]
            )
        return channels

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


def get_metadata(self) -> Dict:
    return self.metadata.to_dict()
