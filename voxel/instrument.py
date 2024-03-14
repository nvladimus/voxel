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
        self.trigger_tree = dict()
        # construct
        self._construct()
        self._find_master_device()

    def _load_device(self, driver: str, module: str, kwds):
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

    def _setup_device(self, device: object, settings: dict):
        """Setup device based on settings dictionary
        :param device: device to be setup
        :param settings: dictionary of attributes, values to set according to config"""
        self.log.info(f'setting up {device}')
        # successively iterate through settings keys
        for key, value in settings.items():
            setattr(device, key, value)

    def _construct_device(self, device_type, device_dictionary):
        """Load, setup, and add any subdevices or tasks of a device
        :param device_type: type of device setting up like camera. Type is specified by yaml
        :param device_dictionary: list of dictionaries describing all alike devices of an instrument
        like [{camera0}, {camera1}]"""
        for name, device in device_dictionary.items():
            self.log.info(f'constructing {name}')
            driver = device['driver']
            module = device['module']
            init = device.get('init', {})
            device_object = self._load_device(driver, module, init)
            settings = device.get('settings', {})
            self._setup_device(device_object, settings)
            device_dict = getattr(self, device_type)
            device_dict[name] = device_object

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
                # If subdevice init needs a serial port, add device's serial port to init arguments
                if parameter.annotation == Serial and Serial in device_object.__dict__.values():
                    device_port_name = [k for k, v in device_object.__dict__.items() if v == Serial]
                    subdevice['init'][name] = getattr(device_object, *device_port_name)
                # If subdevice init needs parent object type, add device object to init arguments
                elif parameter.annotation == type(device_object):
                    subdevice['init'][name] = device_object

        self._construct_device(subdevice_type, subdevice_dictionary)

    def _construct(self):
        """Construct device based on configuration yaml"""

        self.log.info(f'constructing instrument from {self.config_path}')
        for device_type, device_list in self.config['instrument']['devices'].items():
            self._construct_device(device_type, device_list)

    def _find_master_device(self):
        pass
        # # build the tree of device triggers
        for device_type, device_list in self.config['instrument']['devices'].items():
            for name, device in device_list.items():
                master_trigger = device['master_trigger']
                # check if master trigger is a device
                if master_trigger not in [None, 'None', 'none']:
                    # if so, check if there is already a dependent device
                    if master_trigger in self.trigger_tree.keys():
                        # append to the list of dependent devices
                        self.trigger_tree[master_trigger].append({name})
                    else:
                        self.trigger_tree[master_trigger] = [{name}]
        # check if there is more than one master device
        master_device = list()
        for device in self.trigger_tree.keys():
            master_device.append(device)
        if len(master_device) > 1:
            raise ValueError(f'there can only be one master device. but {master_devices} are listed.')
        # find the master device type
        for device_type, device_list in self.config['instrument']['devices'].items():
            for name, device in device_list.items():
                if name == master_device[0]:
                    self.master_device = {'name': name, 'type': device_type}
                    # if daq, we need to figure out the master task
                    if device_type == 'daqs':
                        master_task_dict = dict()
                        for task in device['tasks']:
                            # the master device will not have triggering enabled
                            trigger_mode = device['tasks'][task]['timing']['trigger_mode']
                            if trigger_mode == 'off':
                                self.master_device['task'] = device['tasks'][task]['name']
                                master_task_dict[device['tasks'][task]['name']] = trigger_mode
                        if len(master_task_dict.keys()) > 1:
                            raise ValueError(f'there can only be one master task. but {master_task_dict} are all master tasks.')