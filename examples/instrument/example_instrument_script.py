from voxel.instrument.config import InstrumentConfig
from voxel.instrument.factory import InstrumentFactory
from voxel.instrument.instrument import VoxelInstrument
from voxel.instrument.nidaq import VoxelNIDAQ

CONFIG_YAML = './example_instrument.yaml'


def main():
    config = InstrumentConfig(CONFIG_YAML)
    factory = InstrumentFactory(config)
    instrument: VoxelInstrument = factory.create_instrument()

    print("Testing Instrument Factory...")

    # Test general device creation
    assert len(instrument.devices) == len(config.devices_specs), "Not all devices were created"

    # Test specific device types
    print("\nTesting Cameras:")
    for camera in instrument.cameras.values():
        print(f"  Camera: {camera.name}")
        assert camera.name in config.devices_specs, f"Camera {camera.name} not in config"

    print("\nTesting Lasers:")
    for laser in instrument.lasers.values():
        print(f"  Laser: {laser.name}")
        assert laser.name in config.devices_specs, f"Laser {laser.name} not in config"

    # Test DAQ and tasks
    print("\nTesting DAQ and Tasks:")
    daq = instrument.daq
    assert daq is not None, "DAQ not found in instrument"
    assert isinstance(daq, VoxelNIDAQ), "DAQ is not a VoxelNIDAQ"
    print(f"  DAQ: {daq.name}")

    for task_name, task_specs in config.daq_specs.get('tasks', {}).items():
        task = daq.tasks.get(task_name)
        assert task is not None, f"DAQ Task {task_name} not found"
        print(f"  DAQ Task: {task.name}")

        assert task.task_type == task_specs['task_type'], f"Mismatch in task type for {task_name}"
        assert task.sampling_frequency_hz == task_specs[
            'sampling_frequency_hz'], f"Mismatch in sampling frequency for {task_name}"
        assert task.period_time_ms == task_specs['period_time_ms'], f"Mismatch in period time for {task_name}"
        assert task.rest_time_ms == task_specs['rest_time_ms'], f"Mismatch in rest time for {task_name}"

        for channel in task.channels.values():
            print(f"    Channel: {channel.name}")
            device = instrument.devices.get(channel.name)
            assert device is not None, f"Device {channel.name} not found for channel"
            assert hasattr(device, 'daq_task'), f"Device {device.name} missing daq_task attribute"
            assert hasattr(device, 'daq_channel'), f"Device {device.name} missing daq_channel attribute"
            assert device.daq_task == task, f"Mismatch in daq_task for device {device.name}"
            assert device.daq_channel == channel, f"Mismatch in daq_channel for device {device.name}"

    # Test channels configuration
    print("\nTesting Instrument Channels:")
    for channel_name, channel_config in config.channels.items():
        print(f"  Channel: {channel_name}")
        for device_type, device_name in channel_config.items():
            device = instrument.devices.get(device_name)
            assert device is not None, f"Device {device_name} not found for channel {channel_name}"
            print(f"    {device_type}: {device.name}")

    print("\nAll tests passed successfully!")
    instrument.close()


if __name__ == "__main__":
    main()
