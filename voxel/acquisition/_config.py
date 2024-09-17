from typing import Dict, List, Optional, Tuple, Any

from pydantic import BaseModel, Field, field_validator
from ruamel.yaml import YAML

from voxel.acquisition._definitions import TileAcquisitionStrategy
from voxel.acquisition.model.scan_plan import ScanPathStrategy, StartCorner, Direction, Pattern
from voxel.utils.logging import get_logger


class AcquisitionSpecs(BaseModel):
    step_size: float
    tile_overlap: float = 0.15
    acquisition_strategy: TileAcquisitionStrategy
    channels: List[str]

    @classmethod
    @field_validator('channels')
    def validate_channels(cls, v):
        if not v:
            raise ValueError("At least one channel must be specified")
        return v


class ScanPathKwds(BaseModel):
    start_corner: Optional[StartCorner] = None
    direction: Optional[Direction] = None
    pattern: Optional[Pattern] = None
    reverse: bool = False
    custom_plan: Optional[List[Tuple[int, int]]] = None


class ScanPathSpecs(BaseModel):
    strategy: ScanPathStrategy
    kwds: ScanPathKwds

    @classmethod
    @field_validator('kwds')
    def validate_custom_plan(cls, v, values):
        if values.get('strategy') == ScanPathStrategy.CUSTOM and not v.custom_plan:
            raise ValueError("Custom plan must be provided when strategy is 'custom'")
        return v


class PersistenceSpecs(BaseModel):
    handler: str
    file_path: str

    @classmethod
    @field_validator('handler')
    def validate_handler(cls, v):
        valid_handlers = ['yaml', 'json', 'pickle']
        if v.lower() not in valid_handlers:
            raise ValueError(f"Invalid persistence handler. Must be one of: {valid_handlers}")
        return v.lower()


class MetadataSpecs(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: Dict[str, Any] = {}


class AcquisitionConfig(BaseModel):
    instrument: str
    specs: AcquisitionSpecs
    scan_path: ScanPathSpecs
    persistence: PersistenceSpecs
    metadata: MetadataSpecs

    @classmethod
    def from_yaml(cls, filepath: str) -> 'AcquisitionConfig':
        try:
            yaml = YAML(typ='safe')
            with open(filepath) as f:
                config_data = yaml.load(f)
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")

    def __post_init__(self, **data):
        super().__init__(**data)
        self.log = get_logger(self.__class__.__name__)
