from pathlib import Path
from typing import Any

from pydantic import BaseModel, field_validator
from ruamel.yaml import YAML

from voxel.utils.vec import Vec3D

from .scan_path import ScanDirection, ScanPattern, StartCorner


class AcquisitionSpecs(BaseModel):
    file_path: str
    z_step_size: float
    tile_overlap: float = 0.15
    scan_pattern: ScanPattern = ScanPattern.RASTER
    scan_direction: ScanDirection = ScanDirection.ROW_WISE
    start_corner: StartCorner = StartCorner.TOP_LEFT
    reverse_scan_path: bool = False
    volume_min_corner: str | None = None
    volume_max_corner: str | None = None
    channels: list[str] = ["all"]

    @classmethod
    @field_validator("file_path")
    def validate_file_path(cls, v):
        try:
            with open(v) as file:
                YAML(typ="safe").load(file)
        except Exception as e:
            raise ValueError(f"Invalid file path: {e}")
        return v

    @classmethod
    @field_validator("volume_min_corner", "volume_max_corner")
    def validate_volume_min_corner(cls, v):
        if v is None:
            return None
        try:
            return Vec3D.from_str(v)
        except Exception as e:
            raise ValueError(f"Invalid volume min corner: {e}")


class MetadataSpecs(BaseModel):
    driver: str
    kwds: dict[str, Any] = {}


class FrameStackSpecs(BaseModel):
    idx: str
    pos: str
    size: str
    z_step_size: float | int
    channels: list[str]
    settings: dict[str, Any] = {}


class PlanSpecs(BaseModel):
    frame_stacks: dict[str, FrameStackSpecs]
    scan_path: list[str]


class PlannerConfig(BaseModel):
    instrument: str
    specs: AcquisitionSpecs
    metadata: dict[str, Any] = {}
    plan: PlanSpecs | None = None

    @classmethod
    def from_yaml(cls, file_path: str | Path) -> "PlannerConfig":
        try:
            file_path = Path(file_path)
            loader = YAML(typ="safe")
            with file_path.open() as file:
                data = loader.load(file)

                instrument_str = data.get("instrument", "")

                specs_data = data.get("specs", {})
                specs_data["file_path"] = str(file_path)
                specs = AcquisitionSpecs(**specs_data)

                metadata = data.get("metadata", {})

                if plan := data.get("plan", None):
                    plan = PlanSpecs(**plan)

                return cls(instrument=instrument_str, specs=specs, metadata=metadata, plan=plan)
        except Exception as e:
            raise ValueError(f"Error loading configuration from {file_path}: {e}")

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)
