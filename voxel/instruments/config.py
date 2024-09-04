from typing import Dict, Optional

from device_spinner.config import Config as DeviceSpinnerConfig

from voxel.instruments.definitions import CHANNEL_DEVICES


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
        self.validate()

    def __repr__(self):
        return f"InstrumentConfig({self.cfg})"

    @property
    def instrument_specs(self) -> Optional[Dict]:
        if "module" in self.cfg and "class" in self.cfg:
            return {
                "module": self.cfg["module"],
                "class": self.cfg["class"],
                "kwds": self.cfg.get("kwds", {})
            }

    @property
    def devices_specs(self) -> Dict:
        return dict(self.cfg["devices"])

    @property
    def channels(self) -> Dict:
        return dict(self.cfg["channels"])

    def validate(self):
        errors = []
        if self.cfg is None:
            errors.append("Config file is empty")
        else:
            errors.extend(self._validate_devices())
            errors.extend(self._validate_channels())
        if errors:
            raise InstrumentConfigError("\n".join(errors))

    def _validate_devices(self):
        errors = []
        if "devices" not in self.cfg:
            errors.append("Config file must contain a 'build' key")
        return errors

    def _validate_channels(self):
        errors = []
        if "channels" not in self.cfg:
            errors.append("Config file must contain a 'channels' key")
        for name, devices in self.channels.items():
            for key, device in devices.items():
                if key not in CHANNEL_DEVICES:
                    errors.append(f"Key {key} in channel '{name}' must be one of: {CHANNEL_DEVICES}")
                if device not in self.devices_specs:
                    errors.append(f"Device {device} in channel '{name}' not in your devices schema")
        return errors
