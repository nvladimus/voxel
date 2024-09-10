from voxel import VoxelInstrument
from voxel.acquisition.config import AcquisitionConfig
from voxel.utils.logging import get_logger


class VoxelAcquisition:

    def __init__(self, config: AcquisitionConfig, instrument: VoxelInstrument):
        self.log = get_logger(f"{self.__class__.__name__}")
        self.config = config
        self.instrument = instrument
        self.log.debug(f"Acquisition created with instrument: {instrument}")

