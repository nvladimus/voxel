from typing import Dict

from device_spinner.config import Config as DeviceSpinnerConfig


class InstrumentConfig(DeviceSpinnerConfig):
    def __init__(self, config_file: str) -> None:
        super().__init__(filepath=config_file)
        self.validate()

    def __repr__(self):
        return f"InstrumentConfig({self.cfg})"

    @property
    def devices_schema(self) -> Dict:
        return self.cfg["devices"]

    def validate(self):
        errors = []
        if self.cfg is None:
            errors.append("Config file is empty")
        else:
            errors.extend(self._validate_devices_schema())
        if errors:
            raise ValueError("\n".join(errors))

    def _validate_devices_schema(self):
        errors = []
        if "devices" not in self.cfg:
            errors.append("Config file must contain a 'build' key")
        return errors
