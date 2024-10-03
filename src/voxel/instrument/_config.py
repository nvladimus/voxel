from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, field_validator
from ruamel.yaml import YAML

from voxel.utils.logging import get_logger


class DAQTaskSpecs(BaseModel):
    task_type: str
    sampling_frequency_hz: int
    period_time_ms: float
    rest_time_ms: float


class DAQSpecs(BaseModel):
    conn: str
    tasks: Dict[str, DAQTaskSpecs]
    simulated: bool = False


class DeviceSpec(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: Dict[str, Any] = {}
    daq_channel: Optional[Dict[str, Any]] = None


class WriterSpec(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: Dict[str, Any] = {}


class FileTransferSpec(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: Dict[str, Any] = {}


class ChannelSpec(BaseModel):
    camera: str
    lens: str
    laser: str
    writer: str
    filter_: str = Field(None, alias="filter")
    writer: str
    file_transfer: str


type InstanceSpec = Union[DeviceSpec, WriterSpec, FileTransferSpec]


class InstrumentConfigError(Exception):
    pass


class InstrumentConfig(BaseModel):
    """Instrument configuration class."""
    name: str
    description: Optional[str] = None
    module: str = "voxel.instrument.instrument"
    class_name: str = Field("VoxelInstrument", alias="class")
    instrument_kwds: Dict[str, Any] = Field(default_factory=dict)
    daq: DAQSpecs
    devices: Dict[str, DeviceSpec]
    writers: Dict[str, WriterSpec] = {}
    file_transfers: Dict[str, FileTransferSpec] = Field({}, alias="transfers")
    channels: Dict[str, ChannelSpec] = {}
    settings: Dict[str, Dict[str, Any]] = {}

    @classmethod
    @field_validator('name')
    def sanitize_name(cls, v):
        return v.lower().replace(" ", "_")

    @classmethod
    @field_validator('settings')
    def validate_devices_in_settings(cls, v, info):
        devices = info.data.get('devices', {})
        for device_name in v:
            if device_name not in devices:
                raise ValueError(f"Device {device_name} in settings not found in devices")
        return v

    @classmethod
    @field_validator('channels')
    def validate_channel_items(cls, v, info):
        items = info.data.get('devices', {}) | info.data.get('writers', {}) | info.data.get('transfers', {})
        for channel_name, channel in v.items():
            for item_name in ['camera', 'lens', 'laser', 'writer', 'filter', 'transfer']:
                if channel[item_name] not in items:
                    raise ValueError(
                        f"Item {channel[item_name]} in channel {channel_name} not found in devices, "
                        f"writers or transfers")

    @classmethod
    def from_yaml(cls, config_file: str):
        try:
            yaml = YAML(typ='safe', pure=True)
            with open(config_file, 'r') as f:
                config_data = yaml.load(f)
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")

    def __post_init__(self, **data):
        super().__init__(**data)
        self.log = get_logger(self.__class__.__name__)

    def __repr__(self):
        return f"InstrumentConfig(name={self.name}, devices={len(self.devices)})"
