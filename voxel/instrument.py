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

    def __init__(self, config_filename: str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # current working directory
        this_dir = Path(__file__).parent.resolve()
        self.config_path = this_dir / Path(config_filename)
        #yaml = YAML(typ='safe', pure=True)    # loads yaml in as dict. May want to use in future
        self.config = YAML().load(Path(self.config_path))
        # this device type list is hardcoded by type, perhaps another way to do this
        self.cameras = dict()
        self.tiling_stages = dict()
        self.scanning_stages = dict()
        self.lasers = dict()
        self.filter_wheels = dict()
        self.daqs = dict()
        self.lasers = dict()
        self.combiners = dict()
        self.aotfs = dict()
        self.tunable_lenses = dict()
        # construct
        self.construct()

    def load_device(self, driver: str, module: str, kwds):
        """Load device based on driver, module, and kwds specified
        :param driver: driver of device
        :param module: specific class of device within driver
        :param kwds: keyword argument required in the init of the device"""
        self.log.info(f'loading {driver}.{module}')
        device_class = getattr(importlib.import_module(driver), module)
        # for k, v in kwds.items():
        #     if str(v).split('.')[0] in dir(sys.modules[driver]):
        #         arg_class = getattr(sys.modules[driver], v.split('.')[0])
        #         kwds[k] = getattr(arg_class, '.'.join(v.split('.')[1:]))
        return device_class(**kwds)

    def setup_device(self, device: object, settings: dict):
        """Setup device based on settings dictionary
        :param device: device to be setup
        :param settings: dictionary of attributes, values to set according to config"""
        self.log.info(f'setting up {device}')
        # successively iterate through settings keys
        for key, value in settings.items():
            setattr(device, key, value)

    def construct_device(self, device_type, device_dictionary):
        """Load, setup, and add any subdevices or tasks of a device
        :param device_type: type of device setting up like camera. Type is specified by yaml
        :param device_dictionary: list of dictionaries describing all alike devices of an instrument
        like [{camera0}, {camera1}]"""
        for name, device in device_dictionary.items():
            self.log.info(f'constructing {name}')
            driver = device['driver']
            module = device['module']
            init = device.get('init', {})
            device_object = self.load_device(driver, module, init)
            settings = device.get('settings', {})
            self.setup_device(device_object, settings)
            device_dict = getattr(self, device_type)
            device_dict[name] = device_object

            if 'tasks' in device.keys() and device_type == 'daqs':
                for task_type, task_dict in device['tasks'].items():
                    #TODO: how to deal with pulse count?
                    device_object.add_task(task_dict, task_type[:2] )

            # Add subdevices under device and fill in any needed keywords to init
            for subdevice_type, subdevice_dictionary in device.get('subdevices', {}).items():
                self.construct_subdevice(device_object, subdevice_type, subdevice_dictionary)

    def construct_subdevice(self, device_object, subdevice_type, subdevice_dictionary):
        """Handle the case where devices share serial ports or device objects
        :param device_object: parent device setup before subdevice
        :param subdevice_type: device type of subdevice. Can be different from parent device
        :param subdevice_dictionary: dictionary of all subdevices"""

        for subdevice in subdevice_dictionary.values():
            # Import subdevice class in order to access keyword argument required in the init of the device
            subdevice_class = getattr(importlib.import_module(subdevice['driver']), subdevice['module'])
            subdevice_needs = inspect.signature(subdevice_class.__init__).parameters
            for name, parameter in subdevice_needs.items():
                # If subdevice init needs a serial port, add device's serial port to init arguments
                if parameter.annotation == Serial and Serial in device_object.__dict__.values():
                    device_port_name = [k for k, v in device_object.__dict__.items() if v == Serial]
                    subdevice['init'][name] = getattr(device_object, *device_port_name)
                # If subdevice init needs parent object type, add device object to init arguments
                elif parameter.annotation == type(device_object):
                    subdevice['init'][name] = device_object

        self.construct_device(subdevice_type, subdevice_dictionary)

    def construct(self):
        """Construct device based on configuration yaml"""

        self.log.info(f'constructing instrument from {self.config_path}')
        for device_type, device_list in self.config['instrument']['devices'].items():
            self.construct_device(device_type, device_list)


