from abc import abstractmethod, ABC
from typing import Optional, Dict

from acquisition.metadata.base import VoxelMetadata
from voxel import VoxelInstrument
from voxel.acquisition.config import AcquisitionConfig
from voxel.utils.logging import get_logger


class VoxelAcquisition:

    def __init__(self, config: AcquisitionConfig, instrument: VoxelInstrument, metadata_handler: VoxelMetadata,
                 name: Optional[str] = None):
        self.log = get_logger(f"{self.__class__.__name__}")
        self.name = name
        self.config = config
        self.metadata = metadata_handler
        self.instrument = instrument
        self.channels = self.instrument.channels
        self.log.debug(f"Acquisition created with instrument: {instrument}")

    def get_metadata(self) -> Dict:
        return self.metadata.to_dict()
