from typing import Any

from voxel.acquisition._prev._config import AcquisitionConfig
from voxel.acquisition._prev.acquisition import VoxelAcquisition
from voxel.acquisition.metadata.base import VoxelMetadata
from voxel.acquisition._prev.scan_plan import (
    ScanPathGenerator, ParametricScanPathGenerator, SpiralScanPathGenerator, CustomScanPathGenerator, ScanPathStrategy
)
from voxel.acquisition._prev.persistence import TilePersistenceHandler, YamlifyTiles, JsonifyTiles, PickleTiles
from voxel.instrument import InstrumentConfig, VoxelInstrument, InstrumentFactory
from voxel.utils.logging import get_logger


class AcquisitionFactory:
    def __init__(self, config: AcquisitionConfig) -> None:
        self.config = config
        self.log = get_logger(self.__class__.__name__)
        self.instrument = self._load_instrument()
        self.metadata = self._load_metadata()

    def _load_instrument(self) -> VoxelInstrument:
        try:
            instrument_config = InstrumentConfig.from_yaml(self.config.instrument)
            instrument_factory = InstrumentFactory(instrument_config)
            return instrument_factory.create_instrument()
        except Exception as e:
            raise ValueError(f"Error loading instrument: {e}")

    def _load_metadata(self) -> VoxelMetadata:
        try:
            metadata_class = self._load_class(self.config.metadata.module, self.config.metadata.class_name)
            return metadata_class(**self.config.metadata.kwds)
        except Exception as e:
            raise ValueError(f"Error loading metadata: {e}")

    @staticmethod
    def _load_class(module: str, class_name: str) -> Any:
        try:
            module = __import__(module, fromlist=[class_name])
            return getattr(module, class_name)
        except Exception as e:
            raise ValueError(f"Error loading class: {e}")

    def _create_scan_path_generator(self) -> ScanPathGenerator:
        scan_path_config = self.config.scan_path
        strategy = scan_path_config.strategy
        kwds = scan_path_config.kwds

        if strategy == ScanPathStrategy.PARAMETRIC:
            return ParametricScanPathGenerator(
                start_corner=kwds.start_corner,
                direction=kwds.direction,
                pattern=kwds.pattern,
                reverse=kwds.reverse
            )
        elif strategy == ScanPathStrategy.SPIRAL:
            return SpiralScanPathGenerator(
                start_corner=kwds.start_corner,
                direction=kwds.direction,
                reverse=kwds.reverse
            )
        elif strategy == ScanPathStrategy.CUSTOM:
            return CustomScanPathGenerator(
                custom_plan=kwds.custom_plan
            )
        else:
            raise ValueError(f"Invalid scan path strategy: {strategy}")

    def _create_tile_persistence_handler(self) -> TilePersistenceHandler:
        handler = self.config.persistence.handler
        file_path = self.config.persistence.file_path

        if handler == 'yaml':
            return YamlifyTiles(file_path)
        elif handler == 'json':
            return JsonifyTiles(file_path)
        elif handler == 'pickle':
            return PickleTiles(file_path)
        else:
            raise ValueError(f"Invalid persistence handler: {handler}")

    def create_acquisition(self) -> VoxelAcquisition:
        scan_path_generator = self._create_scan_path_generator()
        tile_persistence_handler = self._create_tile_persistence_handler()

        return VoxelAcquisition(
            specs=self.config.specs,
            instrument=self.instrument,
            metadata_handler=self.metadata,
            scan_path_generator=scan_path_generator,
            tile_persistence_handler=tile_persistence_handler
        )
