from typing import Dict, Optional

from device_spinner.config import Config as DeviceSpinnerConfig

from voxel.instrument.definitions import CHANNEL_DEVICES
from voxel.utils.logging import get_logger


class InstrumentConfigError(Exception):
    pass


class InstrumentConfig(DeviceSpinnerConfig):
    """Instrument configuration class.
    :param config_file: Path to the YAML configuration file.
    :type config_file: str
    :raises InstrumentConfigError: If the configuration file is empty or invalid.
    """

    def __init__(self, config_file: str) -> None:
        super().__init__(filepath=config_file)
        self.log = get_logger(self.__class__.__name__)
        self.validate()

    def __repr__(self):
        return f"InstrumentConfig({self.cfg})"

    @property
    def instrument_specs(self) -> Optional[Dict]:
        return {
            "name": self._sanitize_name(self.cfg.get("name", "instrument")),
            "module": self.cfg.get("module", "voxel.instrument.instrument"),
            "class": self.cfg.get("class", "VoxelInstrument"), "kwds": self.cfg.get("kwds", {})
        }

    @staticmethod
    def _sanitize_name(name: str) -> str:
        return name.lower().replace(" ", "_")

    @property
    def devices_specs(self) -> Dict:
        return dict(self.cfg["devices"])

    @property
    def channels(self) -> Dict:
        return dict(self.cfg["channels"])

    @property
    def daq_specs(self) -> Dict:
        return dict(self.cfg["daq"])

    def startup_settings(self) -> Optional[Dict]:
        if "settings" in self.cfg:
            return dict(self.cfg["settings"])

    def validate(self):
        errors = []
        if self.cfg is None:
            errors.append("Config file is empty")
        else:
            errors.extend(self.validate_daq_specs())
            errors.extend(self._validate_devices())
            errors.extend(self._validate_channels())
        if errors:
            raise InstrumentConfigError("\n".join(errors))

    def _validate_devices(self):
        errors = []
        if "devices" not in self.cfg:
            errors.append("Config file must contain a 'build' key")
        return errors

    def validate_daq_specs(self):
        errors = []
        if "daq" not in self.cfg:
            errors.append("Config file must contain a 'daq' key")
        if "conn" not in self.cfg["daq"]:
            errors.append("DAQ specs must contain a 'conn' key")
        if "tasks" not in self.cfg["daq"]:
            errors.append("DAQ specs must contain a 'tasks' key")
        return errors

    def _validate_channels(self):
        errors = []
        if "channels" not in self.cfg:
            errors.append("Config file must contain a 'channels' key")
        for name, devices in self.channels.items():
            for device_type, device in devices.items():
                if device_type not in CHANNEL_DEVICES:
                    errors.append(f"Key {device_type} in channel '{name}' must be one of: {CHANNEL_DEVICES}")
                if device not in self.devices_specs:
                    errors.append(f"Device {device} in channel '{name}' not in your devices schema")
        return errors
