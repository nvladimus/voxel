from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator
from ruamel.yaml import YAML

from voxel.core.acquisition.model import AcquisitionSpecs
from voxel.core.utils.log_config import get_logger


class MetadataSpecs(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: dict[str, Any] = {}


class DAQTaskSpecs(BaseModel):
    task_type: str
    sampling_frequency_hz: int
    period_time_ms: float
    rest_time_ms: float


class DAQSpecs(BaseModel):
    conn: str
    tasks: dict[str, DAQTaskSpecs]
    simulated: bool = False


class DeviceSpec(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: dict[str, Any] = {}
    daq_channel: dict[str, Any] | None = None


class WriterSpec(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: dict[str, Any] = {}


class FileTransferSpec(BaseModel):
    module: str
    class_name: str = Field(..., alias="class")
    kwds: dict[str, Any] = {}


class ChannelSpec(BaseModel):
    camera: str
    lens: str
    laser: str
    writer: str
    filter_: str = Field(None, alias="filter")
    writer: str
    file_transfer: str


type InstanceSpec = DeviceSpec | WriterSpec | FileTransferSpec


class InstrumentConfig(BaseModel):
    """Instrument configuration class."""

    name: str
    description: str | None = None
    module: str = "voxel.core.instrument.instrument"
    class_name: str = Field("VoxelInstrument", alias="class")
    daq: DAQSpecs
    devices: dict[str, DeviceSpec]
    writers: dict[str, WriterSpec] = {}
    file_transfers: dict[str, FileTransferSpec] = Field({}, alias="transfers")
    channels: dict[str, ChannelSpec] = {}
    settings: dict[str, dict[str, Any]] = {}

    @classmethod
    @field_validator("name")
    def sanitize_name(cls, v):
        return v.lower().replace(" ", "_")

    @classmethod
    @field_validator("settings")
    def validate_devices_in_settings(cls, v, info):
        devices = info.data.get("devices", {})
        for device_name in v:
            if device_name not in devices:
                raise ValueError(f"Device {device_name} in settings not found in devices")
        return v

    @classmethod
    @field_validator("channels")
    def validate_channel_items(cls, v, info):
        items = info.data.get("devices", {}) | info.data.get("writers", {}) | info.data.get("transfers", {})
        for channel_name, channel in v.items():
            for item_name in [
                "camera",
                "lens",
                "laser",
                "writer",
                "filter",
                "transfer",
            ]:
                if channel[item_name] not in items:
                    raise ValueError(
                        f"Item {channel[item_name]} in channel {channel_name} not found in devices, "
                        f"writers or transfers"
                    )

    @classmethod
    def from_yaml(cls, config_file: str) -> "InstrumentConfig":
        try:
            yaml = YAML(typ="safe", pure=True)
            with open(config_file, "r") as f:
                config_data = yaml.load(f)
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")

    def __post_init__(self, **data):
        super().__init__(**data)
        self.log = get_logger(self.__class__.__name__)

    def __repr__(self):
        return f"InstrumentConfig(name={self.name}, devices={len(self.devices)})"


class VoxelConfig(BaseModel):
    instrument: InstrumentConfig
    specs: AcquisitionSpecs
    metadata: MetadataSpecs

    @classmethod
    def from_file(cls, file_path: str | Path) -> "VoxelConfig":
        try:
            file_path = Path(file_path)
            loader = YAML(typ="safe")
            with file_path.open() as file:
                data = loader.load(file)

                # Load InstrumentConfig
                instrument_data = data.get("instrument", {})
                if isinstance(instrument_data, dict):
                    instrument_config = InstrumentConfig(**instrument_data)
                else:
                    instrument_config = InstrumentConfig.from_yaml(file_path.parent / instrument_data)

                # Prepare AcquisitionSpecs
                specs_data = data.get("specs", {})
                specs_data["file_path"] = str(file_path)
                acquisition_specs = AcquisitionSpecs(**specs_data)

                # Prepare MetadataSpecs
                metadata_specs = MetadataSpecs(**data.get("metadata", {}))

                return cls(instrument=instrument_config, specs=acquisition_specs, metadata=metadata_specs)
        except Exception as e:
            raise ValueError(f"Error loading configuration from {file_path}: {e}")


if __name__ == "__main__":
    from pprint import pprint

    config_path = Path(__file__).parent / "config.yaml"

    cfg = VoxelConfig.from_file(config_path)
    pprint(cfg)
