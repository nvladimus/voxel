import logging
import shutil
import datetime
import subprocess
import os
import sys
from pathlib import Path
import inspect
import importlib
from serial import Serial
from ruamel.yaml import YAML

class Instrument:

    def _construct(self):
        """Construct device based on configuration yaml"""

        self.log.info(f'constructing instrument from {self.config_path}')
        # grab instrument id
        try:
            self.id = self.config['instrument']['id']
        except:
            raise ValueError('no instrument id defined. check yaml file.')
        for device_type, device_list in self.config['instrument']['devices'].items():
            setattr(self, device_type, dict())
            self._construct_device(device_type, device_list)

    def _construct_device(self, device_type, device_dictionary):
        """Load, setup, and add any subdevices or tasks of a device
        :param device_type: type of device setting up like camera. Type is specified by yaml
        :param device_dictionary: list of dictionaries describing all alike devices of an instrument
        like [{camera0}, {camera1}]"""
        for name, device in device_dictionary.items():
            self.log.info(f'constructing {name}')
            # add to the master list of devices
            self.device_list[name] = device_type
            driver = device['driver']
            module = device['module']
            init = device.get('init', {})
            device_object = self._load_device(driver, module, init)
            settings = device.get('settings', {})
            self._setup_device(device_object, settings)
            device_dict = getattr(self, device_type)
            device_dict[name] = device_object

            # added logic for daqs
            if 'tasks' in device.keys() and device_type == 'daqs':
                for task_type, task_dict in device['tasks'].items():
                    pulse_count = task_dict['timing'].get('pulse_count', None)
                    device_object.add_task(task_dict, task_type[:2], pulse_count)

            # Add subdevices under device and fill in any needed keywords to init
            for subdevice_type, subdevice_dictionary in device.get('subdevices', {}).items():
                self._construct_subdevice(device_object, subdevice_type, subdevice_dictionary)

    def _construct_subdevice(self, device_object, subdevice_type, subdevice_dictionary):
        """Handle the case where devices share serial ports or device objects
        :param device_object: parent device setup before subdevice
        :param subdevice_type: device type of subdevice. Can be different from parent device
        :param subdevice_dictionary: dictionary of all subdevices"""

        for subdevice in subdevice_dictionary.values():
            # Import subdevice class in order to access keyword argument required in the init of the device
            subdevice_class = getattr(importlib.import_module(subdevice['driver']), subdevice['module'])
            subdevice_needs = inspect.signature(subdevice_class.__init__).parameters
            for name, parameter in subdevice_needs.items():
                # add to the master list of devices
                self.device_list[name] = subdevice_type
                # If subdevice init needs a serial port, add device's serial port to init arguments
                if parameter.annotation == Serial and Serial in device_object.__dict__.values():
                    device_port_name = [k for k, v in device_object.__dict__.items() if v == Serial]
                    subdevice['init'][name] = getattr(device_object, *device_port_name)
                # If subdevice init needs parent object type, add device object to init arguments
                elif parameter.annotation == type(device_object):
                    subdevice['init'][name] = device_object

        self.construct_device(subdevice_type, subdevice_dictionary)
        
    def _load_device(self, driver: str, module: str, kwds):
        """Load device based on driver, module, and kwds specified
        :param driver: driver of device
        :param module: specific class of device within driver
        :param kwds: keyword argument required in the init of the device"""
        self.log.info(f'loading {driver}.{module}')
        device_class = getattr(importlib.import_module(driver), module)
        return device_class(**kwds)

    def _setup_device(self, device: object, settings: dict):
        """Setup device based on settings dictionary
        :param device: device to be setup
        :param settings: dictionary of attributes, values to set according to config"""
        self.log.info(f'setting up {device}')
        # successively iterate through settings keys
        for key, value in settings.items():
            setattr(device, key, value)

    def _verify_instrument(self):
        # assert that only one scanning stage is allowed
        self.log.info(f'verifying instrument configuration')
        num_scanning_stages = len(self.scanning_stages)
        if num_scanning_stages > 1:
            raise ValueError(f'only one scanning stage is allowed but {num_scanning_stages} detected')
        # assert that a NIDAQ must be present
        num_daqs = len(self.daqs)
        if num_daqs < 1:
            raise ValueError(f'at least one daq is required but {num_daqs} detected')
        # assert that a camera must be present
        num_cameras = len(self.cameras)
        if num_cameras < 1:
            raise ValueError(f'at least one camera is required but {num_cameras} detected')
        # # assert that a laser must be present
        # num_lasers = len(self.lasers)
        # if num_lasers < 1:
        #     raise ValueError(f'at least one laser is required but {num_lasers} detected')