from voxel.acquisition.config import AcquisitionConfig, AcquisitionFactory
from voxel.acquisition.manager import VoxelAcquisitionManager
from voxel.acquisition.model.scan_path import plot_scan_path
from voxel.instrument import VoxelInstrument, InstrumentConfig
from voxel.instrument.nidaq.base import VoxelDAQ
from voxel.utils.geometry.vec import Vec3D

ACQUISITION_CONFIG_YAML = './example_acquisition.yaml'


def validate_instrument(instrument: VoxelInstrument, inst_config: InstrumentConfig):
    print(f"Testing Instrument: {instrument.name}...")

    # Test general device creation
    assert len(instrument.devices) == len(inst_config.devices), "Not all devices were created"

    # Test specific device types
    print("\nTesting Cameras:")
    for camera in instrument.cameras.values():
        print(f"  Camera: {camera}")
        assert camera.name in inst_config.devices, f"Camera {camera.name} not in config"

    print("\nTesting Lasers:")
    for laser in instrument.lasers.values():
        print(f"  Laser: {laser}")
        assert laser.name in inst_config.devices, f"Laser {laser.name} not in config"

    # Test DAQ and tasks
    print("\nTesting DAQ and Tasks:")
    daq = instrument.daq
    assert isinstance(daq, VoxelDAQ), "DAQ is not a VoxelNIDAQ"
    print(f"  DAQ: {daq}")

    for task_name, task_specs in inst_config.daq.tasks.items():
        task = daq.tasks.get(task_name)
        assert task is not None, f"DAQ Task {task_name} not found"
        print(f"  DAQ Task: {task}")

        assert task.task_type == task_specs.task_type, f"Mismatch in task type for {task_name}"
        assert task.sampling_frequency_hz == task_specs.sampling_frequency_hz, \
            f"Mismatch in sampling frequency for {task_name}"
        assert task.period_time_ms == task_specs.period_time_ms, f"Mismatch in period time for {task_name}"
        assert task.rest_time_ms == task_specs.rest_time_ms, f"Mismatch in rest time for {task_name}"

    # Test DAQ channels
    print("\nTesting DAQ Channels:")
    for device_name, device_spec in inst_config.devices.items():
        if device_spec.daq_channel:
            device = instrument.devices.get(device_name)
            assert device is not None, f"Device {device_name} not found"
            assert hasattr(device, 'daq_task'), f"Device {device_name} missing daq_task attribute"
            assert hasattr(device, 'daq_channel'), f"Device {device_name} missing daq_channel attribute"
            print(f"  Device {device_name} DAQ channel: {device.daq_channel}")

    # Test writers
    print("\nTesting Writers:")
    for writer_name in inst_config.writers:
        assert writer_name in instrument.writers, f"Writer {writer_name} not created"
        print(f"  Writer: {instrument.writers[writer_name]}")

    # Test file transfers
    print("\nTesting File Transfers:")
    for transfer_name in inst_config.file_transfers:
        assert transfer_name in instrument.file_transfers, f"File transfer {transfer_name} not created"
        print(f"  File Transfer: {instrument.file_transfers[transfer_name]}")

    print("\nAll tests passed successfully!")


def main():
    # Step 1: Load the configuration from YAML file
    print("Loading configuration from YAML file...")
    acq_config = AcquisitionConfig.from_file(ACQUISITION_CONFIG_YAML)
    print(f"Configuration loaded: {acq_config}")

    # step 2: Create an acquisition factory with the loaded configuration
    print("\nCreating acquisition factory...")
    acq_factory = AcquisitionFactory(acq_config)

    # Step 3: Use the factory to create the acquisition
    print("\nCreating acquisition...")
    acq = acq_factory.load_acquisition()

    print(f"Acquisition created: {acq}")

    # Step 4: modify acquisition volume
    acq.volume.min_corner = Vec3D(0, 0, 0)
    acq.volume.max_corner = Vec3D(100, 100, 50)

    # plot scan path
    # plot_scan_path(acq.plan.scan_path, "Scan Path")

    # step 5: Save the acquisition plan to a YAML file
    print("\nSaving acquisition plan to YAML file...")
    acq.save_to_yaml()

    # Load the acquisition plan from the YAML file
    print("\nLoading acquisition plan from YAML file...")
    loaded_acq = VoxelAcquisitionManager.load_from_yaml(acq.instrument, ACQUISITION_CONFIG_YAML)

    # plot_scan_path(loaded_acq.plan.scan_path, "Loaded Scan Path")

    assert acq == loaded_acq, "Loaded acquisition does not match original acquisition"

    # Step 6: Close the instrument (clean up resources)
    print("\nClosing instrument...")
    acq.instrument.close()

    print("\nTest completed successfully!")


if __name__ == "__main__":
    main()
