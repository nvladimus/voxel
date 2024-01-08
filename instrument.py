import logging
import shutil
import datetime
import subprocess
import os
import sys
import ruamel
from pathlib import Path
from spim_core.config_base import Config

class Instrument:

    def __init__(self, config_filename: str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # current working directory
        this_dir = Path(__file__).parent.resolve()
        self.config_path = this_dir / Path(config_filename)
        self.config = Config(str(self.config_path))
        self.cameras = dict()
        self.tiling_stages = dict()
        self.scanning_stages = dict()
        self.lasers = dict()
        self.filter_wheels = dict()
        self.daqs = dict()
        self.construct()

    def load_device(self, driver: str, module: str, kwds: dict = dict()):
        """Load in device based on config. Expecting driver, module, and kwds input"""
        self.log.info(f'loading {driver}.{module}')
        __import__(driver)
        device_class = getattr(sys.modules[driver], module)
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
        for key in settings.keys():
            # determine if key matches an attribute
            if key in dir(device):
                # check if key value is a yaml dictionary
                if type(settings[key]) == ruamel.yaml.comments.CommentedMap:
                    attribute = key
                    # if dictionary, convert to dict and set attribute
                    values = dict(settings[key])
                    setattr(device, attribute, values)
                else:
                    # else set single attribute to single value
                    attribute = key
                    value = settings[key]
                    setattr(device, attribute, value)
            # if no match, check nested settings dictionary
            else:
                nested_settings = settings[key]
                # repeat process of checking nested keys for matches
                for key in nested_settings.keys():
                    if key in dir(device):
                        if type(nested_settings[key]) == ruamel.yaml.comments.CommentedMap:
                            attribute = key
                            values = dict(nested_settings[key])
                            setattr(device, attribute, values)
                        else:
                            attribute = key
                            value = nested_settings[key]
                            setattr(device, attribute, value)
                    else:
                        raise LookupError(f'{key} is not a valid attribute of {type(device)}')

    def construct_cameras(self, cameras_list: list):
        for camera in cameras_list:
            name = camera['name']
            self.log.info(f'constructing {name}')
            driver = camera['driver']
            module = camera['module']
            try:
                init = camera['init']
                camera_object = self.load_device(driver, module, init)
            except:
                camera_object = self.load_device(driver, module)
            try:
                settings = camera['settings']
                self.setup_device(camera_object, settings)
            except:
                self.log.debug('no settings listed')

            self.cameras[name] = camera_object

    def construct_tiling_stages(self, tiling_stages_list: list):
        for tiling_stage in tiling_stages_list:
            name = tiling_stage['name']
            self.log.info(f'constructing {name}')
            driver = tiling_stage['driver']
            module = tiling_stage['module']
            try:
                init = tiling_stage['init']
                tiling_stage_object = self.load_device(driver, module, init)
            except:
                tiling_stage_object = self.load_device(driver, module)
            try:
                settings = tiling_stage['settings']
                self.setup_device(tiling_stage_object, settings)
            except:
                self.log.debug(f'no settings listed')
            self.tiling_stages[name] = tiling_stage_object

    def construct_scanning_stages(self, scanning_stages_list: list):
        for scanning_stage in scanning_stages_list:
            name = scanning_stage['name']
            self.log.info(f'constructing {name}')
            driver = scanning_stage['driver']
            module = scanning_stage['module']
            try:
                init = scanning_stage['init']
                scanning_stage_object = self.load_device(driver, module, init)
            except:
                scanning_stage_object = self.load_device(driver, module)
            try:
                settings = scanning_stage['settings']
                self.setup_device(scanning_stage_object, settings)
            except:
                self.log.debug(f'no settings listed')
            self.scanning_stages[name] = scanning_stage_object

    def construct_filter_wheels(self, filter_wheels_list: list):
        for filter_wheel in filter_wheels_list:
            name = filter_wheel['name']
            self.log.info(f'constructing {name}')
            driver = filter_wheel['driver']
            module = filter_wheel['module']
            try:
                init = filter_wheel['init']
                filter_wheel_object = self.load_device(driver, module, init)
            except:
                filter_wheel_object = self.load_device(driver, module)
            try:
                settings = filter_wheel['settings']
                self.setup_device(filter_wheel_object, settings)
            except:
                self.log.debug(f'no settings listed')
            self.filter_wheels[name] = filter_wheel_object

    def construct_daqs(self, daqs_list: list):
        for daq in daqs_list:
            name = daq['name']
            self.log.info(f'constructing {name}')
            driver = daq['driver']
            module = daq['module']
            init = daq['init']
            id = init['dev']
            daq_object = self.load_device(driver, module, init)
            ao_task = daq['tasks']['ao_task']
            do_task = daq['tasks']['do_task']
            co_task = daq['tasks']['co_task']
            daq_object.add_ao_task(ao_task)
            daq_object.add_do_task(do_task)
            daq_object.add_co_task(co_task)
            self.daqs[name] = daq_object

    def construct(self):
        self.log.info(f'constructing instrument from {self.config_path}')
        for device in self.config.cfg['instrument']['devices'].items():
            device_type = device[0]
            if device_type == 'cameras':
                cameras_list = device[1]
                self.construct_cameras(cameras_list)
            if device_type == 'stages':
                for stage_type in device[1]:
                    if stage_type == 'tiling':
                        tiling_stages_list = device[1][stage_type]
                        self.construct_tiling_stages(tiling_stages_list)
                    elif stage_type == 'scanning':
                        scanning_stages_list = device[1][stage_type]
                        self.construct_scanning_stages(scanning_stages_list) 
            if device_type == 'filter_wheels':
                filter_wheels_list = device[1]
                self.construct_filter_wheels(filter_wheels_list)
            if device_type == 'daqs':
                daqs_list = device[1]
                self.construct_daqs(daqs_list)