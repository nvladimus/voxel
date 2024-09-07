from voxel.devices.nidaq.task import DAQTask
from voxel.instruments.config import InstrumentConfig
from voxel.instruments.factory import InstrumentFactory
from voxel.instruments.instrument import VoxelInstrument

CONFIG_YAML = './instrument_build.yaml'


def main():
    config = InstrumentConfig(CONFIG_YAML)
    factory = InstrumentFactory(config)
    instrument: VoxelInstrument = factory.create_instrument()

    print("Testing Instrument Factory...")

    # Test general device creation
    assert len(instrument.devices) == len(config.devices_specs), "Not all devices were created"

    # Test specific device types
    print("\nTesting Cameras:")
    for _, camera in instrument.cameras.items():
        print(f"  Camera: {camera.name}")
        assert camera.name in config.devices_specs, f"Camera {camera.name} not in config"

    print("\nTesting Lasers:")
    for _, laser in instrument.lasers.items():
        print(f"  Laser: {laser.name}")
        assert laser.name in config.devices_specs, f"Laser {laser.name} not in config"

    # Test DAQ tasks and channels
    print("\nTesting DAQ Tasks and Channels:")
    daq_tasks = [device for device in instrument.devices.values() if isinstance(device, DAQTask)]

    for task in daq_tasks:
        print(f"  DAQ Task: {task.name}")
        assert task.name in config.devices_specs, f"DAQ Task {task.name} not in config"

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
