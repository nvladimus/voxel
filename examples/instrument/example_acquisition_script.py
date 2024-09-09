from examples.instrument.example_instrument_script import validate_instrument
from voxel.acquisition.acquisition import VoxelAcquisition
from voxel.acquisition.config import AcquisitionConfig
from voxel.acquisition.factory import AcquisitionFactory
from voxel.instrument.config import InstrumentConfig

INSTRUMENT_CONFIG_YAML = './example_instrument.yaml'
ACQUISITION_CONFIG_YAML = './example_acquisition.yaml'


def main():
    acq_config = AcquisitionConfig(ACQUISITION_CONFIG_YAML)
    acq: VoxelAcquisition = AcquisitionFactory(acq_config).create_acquisition()

    validate_instrument(acq.instrument, InstrumentConfig(INSTRUMENT_CONFIG_YAML))
    acq.instrument.close()


if __name__ == "__main__":
    main()
