from voxel.acquisition.acquisition import VoxelAcquisition
from voxel.acquisition.config import AcquisitionConfig
from voxel.acquisition._factory import AcquisitionFactory
from voxel.utils.logging import setup_logging


ACQUISITION_CONFIG_YAML = './example_acquisition.yaml'


def main():
    setup_logging(log_level='DEBUG')

    acq_config = AcquisitionConfig(ACQUISITION_CONFIG_YAML)
    acq: VoxelAcquisition = AcquisitionFactory(acq_config).create_acquisition()

    acq.instrument.close()


if __name__ == "__main__":
    main()
