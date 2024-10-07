from dataclasses import dataclass, field, KW_ONLY
from typing import TypedDict, List, Optional

from pydantic import BaseModel


class MetadataNameFormat(TypedDict):
    delimiter: str
    properties: List[str]


@dataclass
class VoxelMetadata:
    instrument_name: str
    experiment_id: str
    subject_id: str
    experimenter_full_name: str
    name_format: Optional[MetadataNameFormat]

    def __post_init__(self):
        if not self.name_format:
            self.name_format = {"delimiter": "_", "properties": ["instrument_type", "subject_id"]}
        if not self.name_format["properties"]:
            raise ValueError("Name format must contain at least one property.")
        for prop in self.name_format["properties"]:
            if not hasattr(self, prop):
                raise ValueError(f"Property {prop} not found in metadata.")

    @property
    def name(self):
        return self.name_format["delimiter"].join([str(getattr(self, prop)) for prop in self.name_format["properties"]])

    def to_dict(self):
        return {
            "instrument_name": self.instrument_name,
            "experiment_id": self.experiment_id,
            "subject_id": self.subject_id,
            "experimenter_full_name": self.experimenter_full_name,
        }


# class VoxelMetadata(BaseModel):
#     instrument_name: str
#     experiment_id: str
#     subject_id: str
#     experimenter_full_name: str
#     name_format: Optional[MetadataNameFormat] = None
#
#     def __init__(self, **data):
#         if not self.name_format:
#             self.name_format = {
#                 'delimiter': '_',
#                 'properties': ['instrument_type', 'subject_id']
#             }
#         if not self.name_format['properties']:
#             raise ValueError("Name format must contain at least one property.")
#         for prop in self.name_format['properties']:
#             if prop not in data:
#                 raise ValueError(f"Property {prop} not found in metadata.")
#         super().__init__(**data)
#
#     @property
#     def name(self):
#         return self.name_format['delimiter'].join(
#             [str(getattr(self, prop)) for prop in self.name_format['properties']])
#
#     def to_dict(self):
#         return {
#             "instrument_name": self.instrument_name,
#             "experiment_id": self.experiment_id,
#             "subject_id": self.subject_id,
#             "experimenter_full_name": self.experimenter_full_name,
#         }
