from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional

from voxel.acquisition.plan.metadata import VoxelMetadata, MetadataNameFormat


class DateTimeFormat(StrEnum):
    ISO = "Year/Month/Day/Hour/Minute/Second"
    US = "Month/Day/Year/Hour/Minute/Second"
    US_NO_TIME = "Month/Day/Year"
    ISO_NO_TIME = "Day/Month/Year"


class AnatomicalDirection(StrEnum):
    ANTERIOR_POSTERIOR = "anterior_to_posterior"
    POSTERIOR_ANTERIOR = "posterior_to_anterior"
    SUPERIOR_INFERIOR = "superior_to_inferior"
    INFERIOR_SUPERIOR = "inferior_to_superior"
    LEFT_RIGHT = "left_to_right"
    RIGHT_LEFT = "right_to_left"


class Medium(StrEnum):
    AIR = "air"
    MULTI = "multi"
    OIL = "oil"
    PBS = "PBS"
    WATER = "water"
    OTHER = "other"


DATE_FORMATS: dict[DateTimeFormat, str] = {
    DateTimeFormat.ISO: "%Y-%m-%d_%H:%M:%S",
    DateTimeFormat.US: "%m-%d-%Y_%H:%M:%S",
    DateTimeFormat.US_NO_TIME: "%m-%d-%Y",
    DateTimeFormat.ISO_NO_TIME: "%Y-%m-%d",
}

ANATOMICAL_DIRECTIONS = {
    AnatomicalDirection.ANTERIOR_POSTERIOR: "Anterior_to_posterior",
    AnatomicalDirection.POSTERIOR_ANTERIOR: "Posterior_to_anterior",
    AnatomicalDirection.SUPERIOR_INFERIOR: "Superior_to_inferior",
    AnatomicalDirection.INFERIOR_SUPERIOR: "Inferior_to_superior",
    AnatomicalDirection.LEFT_RIGHT: "Left_to_right",
    AnatomicalDirection.RIGHT_LEFT: "Right_to_left",
}


@dataclass
class AINDMetadata(VoxelMetadata):
    """
    Metadata matching the AIND standard.
    """

    instrument_name: str
    experiment_id: str
    subject_id: str
    experimenter_full_name: str
    name_format: Optional[MetadataNameFormat]
    date_format: DateTimeFormat
    x_anatomical_direction: AnatomicalDirection
    y_anatomical_direction: AnatomicalDirection
    z_anatomical_direction: AnatomicalDirection
    details: dict = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        directions = [self.x_anatomical_direction, self.y_anatomical_direction, self.z_anatomical_direction]
        if len(set(directions)) != 3:
            raise ValueError("Anatomical directions must be unique.")

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            **{
                "date_format": self.date_format.value,
                "x_anatomical_direction": self.x_anatomical_direction.value,
                "y_anatomical_direction": self.y_anatomical_direction.value,
                "z_anatomical_direction": self.z_anatomical_direction.value,
            },
            **self.details,
        }
