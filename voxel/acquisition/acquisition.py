import logging

from voxel import VoxelInstrument
from voxel.acquisition.config import AcquisitionConfig


class VoxelAcquisition:

    def __init__(self, config: AcquisitionConfig, instrument: VoxelInstrument, log_level='INFO'):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.log.setLevel(log_level)

        self.config = config
        self.instrument = instrument
