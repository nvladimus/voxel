from pydantic import BaseModel, field_validator
from ruamel.yaml import YAML

from voxel.acquisition.model.scan_path import ScanPattern, ScanDirection, StartCorner
from voxel.utils.geometry.vec import Vec3D


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
