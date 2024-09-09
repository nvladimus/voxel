from device_spinner.config import Config as DeviceSpinnerConfig


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
        self.validate()

    def __repr__(self):
        return f"AcquisitionConfig({self.cfg})"

    def validate(self):
        errors = []
        if self.cfg is None:
            errors.append("Config file is empty")
        else:
            errors.extend(self._validate_build_filepath())
        if errors:
            raise AcquisitionConfigError("\n".join(errors))

    def _validate_build_filepath(self):
        errors = []
        if "instrument" not in self.cfg:
            errors.append("Config file must contain a 'instrument' key with the path to the instrument yaml file")
        if not isinstance(self.cfg["instrument"], str):
            errors.append(f"Config file 'instrument' key expected a string `path_to_instrument.yaml`. "
                          f"Got: {self.cfg['instrument']}")
        return errors

    @property
    def instrument_yaml(self) -> str:
        return self.cfg["instrument"]
