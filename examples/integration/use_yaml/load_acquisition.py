from voxel.factory import AcquisitionConfig, AcquisitionFactory
from voxel.acquisition.manager import VoxelAcquisitionManager
from voxel.acquisition.model.scan_path import plot_scan_path
from voxel.instrument import VoxelInstrument, InstrumentConfig
from voxel.instrument.daq.base import VoxelDAQ
from voxel.utils.geometry.vec import Vec3D

ACQUISITION_CONFIG_YAML = "./example_acquisition.yaml"


def get_acquisition_manager() -> VoxelAcquisitionManager:
    # Step 1: Load the configuration from YAML file
    acq_config = AcquisitionConfig.from_file(ACQUISITION_CONFIG_YAML)

    # step 2: Create an acquisition factory with the loaded configuration
    acq_factory = AcquisitionFactory(acq_config)

    # Step 3: Use the factory to load and build the acquisition manager
    acq = acq_factory.load_acquisition()

    return acq


def main():
    acq = get_acquisition_manager()

    acq.volume.min_corner = Vec3D(0, 0, 0)
    acq.volume.max_corner = Vec3D(100, 100, 50)

    # plot scan path
    plot_scan_path(acq.plan.scan_path, "Scan Path")

    # Save the acquisition manager to the YAML file
    acq.save_to_yaml()

    # Load the acquisition plan from the YAML file
    loaded_acq = VoxelAcquisitionManager.load_from_yaml(acq.instrument, ACQUISITION_CONFIG_YAML)

    plot_scan_path(loaded_acq.plan.scan_path, "Loaded Scan Path")

    assert acq == loaded_acq, "Loaded acquisition does not match original acquisition"

    acq.instrument.close()


if __name__ == "__main__":
    main()
