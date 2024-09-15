from acquisition.metadata.base import VoxelMetadata
from voxel.instrument import InstrumentConfig, VoxelInstrument, InstrumentFactory
from voxel.acquisition.acquisition import VoxelAcquisition
from voxel.acquisition.config import AcquisitionConfig
from voxel.utils.logging import get_logger


class AcquisitionFactory:
    def __init__(self, config: AcquisitionConfig):
        self.log = get_logger(self.__class__.__name__)
        self._config = config

    def create_acquisition(self) -> VoxelAcquisition:
        instrument: VoxelInstrument = self._create_instrument()
        metadata_handler: VoxelMetadata = self._create_metadata_handler()
        return VoxelAcquisition(config=self._config, instrument=instrument, metadata_handler=metadata_handler)

    def _create_instrument(self) -> VoxelInstrument:
        config = InstrumentConfig(self._config.instrument_yaml)
        factory = InstrumentFactory(config)
        return factory.create_instrument()

    def _create_metadata_handler(self) -> VoxelMetadata:
        metadata_config = self._config.metadata()
        module = __import__(metadata_config['module'])
        cls = getattr(module, metadata_config['class'])
        return cls(**metadata_config['kwds'])
