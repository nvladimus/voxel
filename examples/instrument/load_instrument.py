from voxel.acquisition.planner import AcquisitionPlanner
from voxel.acquisition.scan_path import ScanPattern, ScanDirection, StartCorner, plot_scan_path
from voxel.instrument import VoxelInstrument, InstrumentConfig, InstrumentFactory
from voxel.instrument.nidaq.base import VoxelDAQ
from voxel.utils.geometry.vec import Vec3D

INSTRUMENT_CONFIG_YAML = './example_instrument.yaml'


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
    inst_config = InstrumentConfig.from_yaml(INSTRUMENT_CONFIG_YAML)
    print(f"Configuration loaded: {inst_config}")

    # Step 2: Create an instrument factory with the loaded configuration
    print("\nCreating instrument factory...")
    instrument_factory = InstrumentFactory(inst_config)

    # Step 3: Use the factory to create the instrument
    print("\nCreating instrument...")
    instrument: VoxelInstrument = instrument_factory.create_instrument()
    print(f"Instrument created: {instrument}")

    # Step 4: Validate the created instrument
    print("\nValidating instrument...")
    validate_instrument(instrument, inst_config)

    z_step_size = 0.5
    channel_names = ['red', 'green']

    planner = AcquisitionPlanner(instrument, z_step_size, channel_names, './acquisition_plan.yaml')

    # Modify volume
    planner.volume.min_corner = Vec3D(0, 0, 0)
    planner.volume.max_corner = Vec3D(100, 100, 50)

    # plot_scan_path(planner.plan.scan_path, "Raster Scan Path")

    planner.scan_pattern = ScanPattern.SERPENTINE
    # plot_scan_path(planner.plan.scan_path, "Serpentine Scan Path")

    planner.scan_direction = ScanDirection.COLUMN_WISE
    # plot_scan_path(planner.plan.scan_path, "Column-wise Serpentine Scan Path")

    planner.start_corner = StartCorner.BOTTOM_RIGHT
    # plot_scan_path(planner.plan.scan_path, "Bottom-right Column-wise Serpentine Scan Path")

    planner.reverse_scan_path = True
    # plot_scan_path(planner.plan.scan_path, "Reversed Bottom-right Column-wise Serpentine Scan Path")

    planner.reverse_scan_path = False
    planner.scan_pattern = ScanPattern.SPIRAL
    # plot_scan_path(planner.plan.scan_path, "Spiral Scan Path")

    planner.start_corner = StartCorner.TOP_RIGHT
    # plot_scan_path(planner.plan.scan_path, "Top-right Spiral Scan Path")

    planner.reverse_scan_path = True
    # plot_scan_path(planner.plan.scan_path, "Reversed Top-right Spiral Scan Path")

    # from pprint import pprint
    planner.save_to_yaml()
    loaded_planner = AcquisitionPlanner.load_from_yaml(instrument, './acquisition_plan.yaml')

    plot_scan_path(loaded_planner.plan.scan_path, "Loaded Spiral Scan Path")

    assert planner == loaded_planner, "Loaded plan does not match original plan"

    # Step 5: Close the instrument (clean up resources)
    print("\nClosing instrument...")
    instrument.close()

    print("\nTest completed successfully!")


if __name__ == "__main__":
    main()
