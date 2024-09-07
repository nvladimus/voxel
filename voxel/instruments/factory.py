import importlib
import logging
from typing import Dict, Any

from voxel.devices import VoxelDevice
from voxel.instruments.config import InstrumentConfig
from voxel.instruments.instrument import VoxelInstrument


class InstrumentFactory:
    def __init__(self, config: InstrumentConfig):
        self.log = logging.getLogger(self.__class__.__name__)
        self._config = config
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
        return cls(config=self._config, devices=self._devices, channels=self._config.channels, **kwds)

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
            self._devices[instance_name] = device_class(**kwargs)
            self.log.debug(f"Successfully created device: {instance_name}")
        except Exception as e:
            self.log.error(f"Error creating device {instance_name}: {str(e)}")
            raise

        return self._devices[instance_name]
