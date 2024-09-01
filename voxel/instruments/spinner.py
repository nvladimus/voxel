from typing import Dict, Any
import importlib
import logging

from voxel.instruments.config import InstrumentConfig


class InstrumentSpinner:
    def __init__(self, config: InstrumentConfig):
        self.log = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.devices: Dict[str, Any] = {}
        self._generate_device_tree()

    def _generate_device_tree(self) -> Dict[str, Any]:
        devices_schema = self.config.devices_schema

        # Create all devices
        for instance_name in devices_schema:
            self._create_device(instance_name, devices_schema)

        # Set config for all devices
        for instance in self.devices.values():
            instance.config = self.config

        return self.devices

    def _create_device(self, instance_name: str, devices_schema: Dict[str, Any]):
        if instance_name in self.devices:
            return self.devices[instance_name]

        self.log.debug(f"Creating device: {instance_name}")

        instance_specs = devices_schema[instance_name]
        module = importlib.import_module(instance_specs['module'])
        device_class = getattr(module, instance_specs['class'])

        # Prepare keyword arguments
        kwargs = instance_specs.get('kwds', {}).copy()

        # Recursively create and replace device dependencies
        for key, value in kwargs.items():
            if isinstance(value, str) and value in devices_schema:
                kwargs[key] = self._create_device(value, devices_schema)

        # Add 'id' to kwargs if not present
        if 'id' not in kwargs:
            kwargs['id'] = instance_name

        # Initialize the device
        try:
            self.devices[instance_name] = device_class(**kwargs)
            self.log.debug(f"Successfully created device: {instance_name}")
        except Exception as e:
            self.log.error(f"Error creating device {instance_name}: {str(e)}")
            raise

        return self.devices[instance_name]

    def create_instrument(self):
        # Implement your instrument creation logic here
        pass