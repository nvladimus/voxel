import importlib
import logging
from typing import Dict, Any

from voxel.devices import VoxelDevice
from voxel.devices.nidaq.ni import VoxelNIDAQ
from voxel.devices.nidaq.task import DAQTask
from voxel.instruments.config import InstrumentConfig
from voxel.instruments.instrument import VoxelInstrument


class InstrumentFactory:
    def __init__(self, config: InstrumentConfig):
        self.log = logging.getLogger(self.__class__.__name__)
        self._config = config
        self._daq = self._create_daq()
        self._daq_tasks = self._create_daq_tasks()
        self._devices: Dict[str, VoxelDevice] = {}
        self._generate_device_instances()

    def create_instrument(self):
        if not self._devices and not self._config.devices_specs:
            self.log.warning("Instrument has no devices based on the _config file")
        if not self._config.instrument_specs:
            cls = VoxelInstrument
            kwds = {}
        else:
            module = importlib.import_module(self._config.instrument_specs['module'])
            cls = getattr(module, self._config.instrument_specs['class'])
            kwds = self._config.instrument_specs.get('kwds', {})
        return cls(config=self._config, devices=self._devices, channels=self._config.channels, daq=self._daq)

    def _create_daq(self):
        name = self._config.cfg.get('name', 'instrument').lower().replace(' ', '_')
        name = f'{name}_daq'
        if not self._config.daq_specs:
            return None
        if 'module' in self._config.daq_specs and 'class' in self._config.daq_specs:
            module = importlib.import_module(self._config.daq_specs['module'])
            cls = getattr(module, self._config.daq_specs['class'])
        else:
            module = importlib.import_module('voxel.devices.nidaq.ni')
            cls = getattr(module, 'VoxelNIDAQ')
        conn = self._config.daq_specs.get('conn', None)
        simulated = self._config.daq_specs.get('simulated', False)
        return cls(name=name, conn=conn, simulated=simulated)

    def _create_daq_tasks(self):
        if not self._daq:
            self._daq = self._create_daq()
        tasks = {}
        for task_name, task_specs in self._config.daq_specs.get('tasks', {}).items():
            tasks[task_name] = DAQTask(
                name=task_name,
                task_type=task_specs['task_type'],
                sampling_frequency_hz=task_specs['sampling_frequency_hz'],
                period_time_ms=task_specs['period_time_ms'],
                rest_time_ms=task_specs['rest_time_ms'],
                daq=self._daq
            )
        return tasks

    def _generate_device_instances(self) -> Dict[str, VoxelDevice]:
        devices_schema = self._config.devices_specs

        # Create all devices
        for instance_name in devices_schema:
            self._create_device(instance_name, devices_schema)

        # Set _config for all devices
        for instance in self._devices.values():
            instance.config = self._config

        return self._devices

    def _create_device(self, instance_name: str, devices_schema: Dict[str, Any]):

        if instance_name in self._devices:
            return self._devices[instance_name]

        self.log.debug(f"Creating device: {instance_name}")

        instance_specs = devices_schema[instance_name]
        module = importlib.import_module(instance_specs['module'])
        device_class = getattr(module, instance_specs['class'])
        assert issubclass(device_class, VoxelDevice)

        # Prepare keyword arguments
        kwargs = instance_specs.get('kwds', {}).copy()

        # Recursively create and replace device dependencies
        for key, value in kwargs.items():
            if isinstance(value, str) and value in devices_schema:
                kwargs[key] = self._create_device(value, devices_schema)

        # Add 'name' to kwargs if not present
        if 'name' not in kwargs:
            kwargs['name'] = instance_name

        # Initialize the device
        try:
            device = device_class(**kwargs)
            self._devices[instance_name] = device
            self.log.debug(f"Successfully created device: {instance_name}")

            # Handle DAQ channel creation if specified
            if 'daq_channel' in instance_specs:
                self._create_daq_channel(device, instance_specs['daq_channel'])

        except Exception as e:
            self.log.error(f"Error creating device {instance_name}: {str(e)}")
            raise

        return self._devices[instance_name]

    def _create_daq_channel(self, device: VoxelDevice, daq_channel_specs: Dict[str, Any]):
        task_name = daq_channel_specs['task']

        # Add the channel to the task
        try:
            task = self._daq_tasks[task_name]
            assert isinstance(task, DAQTask)
            channel = task.add_channel(
                name=device.name,
                port=daq_channel_specs['port'],
                waveform_type=daq_channel_specs['waveform_type'],
                center_volts=daq_channel_specs['center_volts'],
                amplitude_volts=daq_channel_specs['amplitude_volts'],
                start_time_ms=daq_channel_specs['start_time_ms'],
                end_time_ms=daq_channel_specs['end_time_ms'],
                cut_off_frequency_hz=daq_channel_specs['cut_off_freq_hz']
            )
            self.log.info(f"Added DAQ channel for device '{device.name}' to task '{task_name}'")

            # Add daq_task and daq_channel attributes to the device
            device.daq_task = task
            device.daq_channel = channel
        except KeyError:
            self.log.error(f"Task '{task_name}' not found for device '{device.name}'")
        except AssertionError:
            self.log.error(f"Device '{device.name}' is not a DAQTask")
