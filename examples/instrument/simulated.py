from voxel.instruments.config import InstrumentConfig
from voxel.instruments.spinner import InstrumentSpinner

CONFIG_YAML = './simulated.yaml'

if __name__ == "__main__":
    from pprint import pprint

    instrument_config = InstrumentConfig(CONFIG_YAML)
    instrument_spinner = InstrumentSpinner(instrument_config)
    pprint(instrument_config.devices_schema)
    pprint(instrument_spinner.devices.keys())
