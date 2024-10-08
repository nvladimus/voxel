from typing import Any

from pydantic import BaseModel, Field
from ruamel.yaml import YAML

from voxel.acquisition.manager import VoxelAcquisitionManager
from voxel.acquisition.metadata.base import VoxelMetadata
from voxel.acquisition.model.specs import AcquisitionSpecs
from voxel.instrument import VoxelInstrument, InstrumentConfig, InstrumentFactory
from voxel.utils.logging import get_logger


class MetadataSpecs(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: dict[str, Any] = {}


class AcquisitionConfig(BaseModel):
    instrument: str
    specs: AcquisitionSpecs
    metadata: MetadataSpecs

    @classmethod
    def from_file(cls, file_path: str) -> "AcquisitionConfig":
        try:
            loader = YAML(typ="safe")
            with open(file_path) as file:
                data = loader.load(file)
                data["specs"]["file_path"] = file_path
            class_ = cls(**data)
            return class_
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")


class AcquisitionFactory:
    def __init__(self, config: AcquisitionConfig, instrument: VoxelInstrument | None = None) -> None:
        self.instrument
        self.config = config
        self.log = get_logger(self.__class__.__name__)

    def load_acquisition(self) -> VoxelAcquisitionManager:
        return VoxelAcquisitionManager(
            instrument=self._build_instrument(),
            specs=self.config.specs,
            channel_names=self.config.channels,
        )

    def _build_instrument(self) -> VoxelInstrument:
        try:
            instrument_config = InstrumentConfig.from_yaml(self.config.instrument)
            instrument_factory = InstrumentFactory(instrument_config)
            return instrument_factory.create_instrument()
        except Exception as e:
            raise ValueError(f"Error loading instrument: {e}")

    def _build_metadata(self) -> VoxelMetadata:
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
