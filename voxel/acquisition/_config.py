from typing import Dict, Any, List

from pydantic import BaseModel, Field
from ruamel.yaml import YAML

from voxel.acquisition._definitions import TileAcquisitionStrategy
from voxel.acquisition.acquisition import VoxelAcquisition
from voxel.acquisition.metadata.base import VoxelMetadata
from voxel.instrument import InstrumentConfig, InstrumentFactory, VoxelInstrument
from voxel.utils.logging import get_logger


class AcquisitionSpecs(BaseModel):
    step_size: float
    channels: List[str]
    tile_overlap: float = 0.15
    acquisition_strategy: TileAcquisitionStrategy = TileAcquisitionStrategy.ONE_SHOT
    persistence_handler: str
    scan_path_strategy: str


class MetadataSpecs(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: Dict[str, str] = {}


class AcquisitionConfig(BaseModel):
    """Acquisition configuration class."""
    instrument_yaml: str
    acquisition: AcquisitionSpecs
    metadata: MetadataSpecs

    @classmethod
    def from_yaml(cls, filepath: str) -> 'AcquisitionConfig':
        try:
            yaml = YAML(typ='safe')
            with open(filepath, 'r') as f:
                config_data = yaml.load(f)
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")

    def __init__(self, **data):
        super().__init__(**data)
        self.log = get_logger(self.__class__.__name__)
