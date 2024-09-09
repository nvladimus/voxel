from voxel import InstrumentConfig, VoxelInstrument, InstrumentFactory
from voxel.acquisition.acquisition import VoxelAcquisition
from voxel.acquisition.config import AcquisitionConfig
from voxel.utils.logging_config import get_logger


class AcquisitionFactory:
    def __init__(self, config: AcquisitionConfig):
        self.log = get_logger(self.__class__.__name__)
        self._config = config

    def create_acquisition(self) -> VoxelAcquisition:
        instrument: VoxelInstrument = self._create_instrument()
        return VoxelAcquisition(config=self._config, instrument=instrument)

    def _create_instrument(self) -> VoxelInstrument:
        config = InstrumentConfig(self._config.instrument_yaml)
        factory = InstrumentFactory(config)
        return factory.create_instrument()
