from typing import Any

from acquisition.metadata.base import VoxelMetadata
from voxel.acquisition.acquisition import VoxelAcquisition
from voxel.acquisition._config import AcquisitionConfig
from voxel.instrument import InstrumentConfig, VoxelInstrument, InstrumentFactory
from voxel.utils.logging import get_logger


class AcquisitionFactory:
    """Acquisition factory class."""

    def __init__(self, config: AcquisitionConfig) -> None:
        self.config = config
        self.log = get_logger(self.__class__.__name__)
        self.instrument = self._load_instrument()
        self.metadata = self._load_metadata()

    def _load_instrument(self) -> VoxelInstrument:
        try:
            instrument_config = InstrumentConfig.from_yaml(self.config.instrument_yaml)
            instrument_factory = InstrumentFactory(instrument_config)
            return instrument_factory.create_instrument()
        except Exception as e:
            raise ValueError(f"Error loading instrument: {e}")

    def _load_metadata(self) -> VoxelMetadata:
        try:
            metadata = self._load_class(self.config.metadata.module, self.config.metadata.class_name)
            return metadata(**self.config.metadata.kwds)
        except Exception as e:
            raise ValueError(f"Error loading metadata: {e}")

    @staticmethod
    def _load_class(module: str, class_name: str) -> Any:
        try:
            module = __import__(module)
            return getattr(module, class_name)
        except Exception as e:
            raise ValueError(f"Error loading class: {e}")

    def create_acquisition(self) -> 'VoxelAcquisition':
        return VoxelAcquisition(self.config.acquisition, self.instrument, self.metadata)
