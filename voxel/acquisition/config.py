from typing import List, Dict, Any

from device_spinner.config import Config as DeviceSpinnerConfig

from voxel.instrument import VoxelDeviceType
from voxel.utils.logging import get_logger

CHANNEL_DEVICES = [VoxelDeviceType.CAMERA, VoxelDeviceType.LENS, VoxelDeviceType.LASER, VoxelDeviceType.FILTER]


class AcquisitionConfigError(Exception):
    pass


class AcquisitionConfig(DeviceSpinnerConfig):
    """
    Acquisition configuration class.
    :param config_file: Path to the YAML configuration file.
    :type config_file: str
    :raises AcquisitionConfigError: If the configuration file is empty or invalid.
    """

    def __init__(self, config_file: str) -> None:
        super().__init__(filepath=config_file)
        self.log = get_logger(self.__class__.__name__)
        self.validate()

    def __repr__(self):
        return f"AcquisitionConfig({self.cfg})"

    def validate(self):
        errors = []
        warnings = []
        if self.cfg is None:
            errors.append("Config file is empty")
        else:
            if not self.cfg["settings"]:
                warnings.append("Config file must contain a 'settings' key with the path to the settings yaml file")
            errors.extend(self._validate_instrument_yaml_filepath())
            errors.extend(self._validate_file_handling())
        if warnings:
            self.log.warning("\n".join(warnings))
        if errors:
            raise AcquisitionConfigError("\n".join(errors))

    def _validate_instrument_yaml_filepath(self):
        errors = []
        if "instrument" not in self.cfg:
            errors.append("Config file must contain a 'instrument' key with the path to the instrument yaml file")
        if not isinstance(self.cfg["instrument"], str):
            errors.append(f"Config file 'instrument' key expected a string `path_to_instrument.yaml`. "
                          f"Got: {self.cfg['instrument']}")
        return errors

    def _validate_acquisition_specs(self):
        errors = []
        if "acquisition" in self.cfg:
            if not isinstance(self.cfg["acquisition"], Dict):
                errors.append(f"Config file 'acquisition' key expected a dictionary. "
                              f"Got: {self.cfg['acquisition']}")
            if "step_size" not in self.cfg["acquisition"]:
                errors.append("Config file 'acquisition' key must contain a 'step_size' key")
        return errors

    def _validate_channel_specs(self):
        errors = []
        if "channels" not in self.cfg:
            errors.append("Config file must contain a 'channels' key")
        for name, devices in self.cfg["channels"].items():
            for device_type, device in devices.items():
                if device_type not in CHANNEL_DEVICES:
                    errors.append(f"Key {device_type} in channel '{name}' must be one of: {CHANNEL_DEVICES}")
                    # FIXME: add more validation here
        return errors

    def _validate_file_handling(self):
        errors = []
        if "file_handling" in self.cfg:
            if not isinstance(self.cfg["file_handling"], Dict):
                errors.append(f"Config file 'file_handling' key expected a list of dictionaries. "
                              f"Got: {self.cfg['file_handling']}")
            # Maybe add more validation here
        return errors

    @property
    def instrument_yaml(self) -> str:
        return self.cfg["instrument"]

    @property
    def settings_path(self) -> str:
        return self.cfg.get("settings", "")

    @property
    def acquisition_specs(self) -> Dict[str, Any]:
        return self.cfg.get("acquisition", {})

    @property
    def channel_specs(self) -> Dict[str, Dict[str, Any]]:
        return self.cfg.get("channels", {})

    def metadata(self) -> Dict[str, Any]:
        return self.cfg.get("metadata", {})

    # FIXME: refine the return type
    @property
    def file_handling_specs(self) -> List[Dict[str, Dict[str, Any]]]:
        return self.cfg.get("file_handling", {})
