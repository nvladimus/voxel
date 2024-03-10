import logging
import shutil
import datetime
import subprocess
import os
import sys
import inspect
import importlib
from pathlib import Path
from serial import Serial
from ruamel.yaml import YAML
from voxel.instruments.instrument import Instrument

class ExASPIM(Instrument):

    def __init__(self, config_filename: str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # current working directory
        this_dir = Path(__file__).parent.resolve()
        self.config_path = this_dir / Path(config_filename)
        #yaml = YAML(typ='safe', pure=True)    # loads yaml in as dict. May want to use in future
        self.config = YAML().load(Path(self.config_path))
        # store a dict of {device name: device type} for convenience
        self.device_list = dict()
        # construct microscope
        self._construct()
        # verify constructed microscope
        self._verify_instrument()
        # verify master device for microscope
        self._verify_master_device()
        # verify channels for microscope
        self._verify_channels()

    def _verify_channels(self):
        setattr(self, 'channels', dict())
        for channel_name, channel in self.config['instrument']['channels'].items():
            self.channels[channel_name] = {
                'laser': channel['laser'],
                'filter_wheel': channel['filter_wheel']
            }

    def _verify_master_device(self):

        for device_type, device_list in self.config['instrument']['devices'].items():
            # check if this is the master device
            for name, device in device_list.items():
                if 'master' in device.keys():
                    setattr(self, 'master_device', dict())
                    self.log.info(f'loading {name} as a {device_type} master device')
                    if isinstance(device['master'], bool):
                        if device['master'] == True and not self.master_device:
                            self.master_device['name'] = name
                            self.master_device['type'] = device_type  
                            # added logic for daqs
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
                        else:
                            raise ValueError('master device is already defined. only one master device is allowed.')
                    else:
                        raise ValueError('master must be defined as true or false.')

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
        # assert that a laser must be present
        num_lasers = len(self.lasers)
        if num_lasers < 1:
            raise ValueError(f'at least one laser is required but {num_lasers} detected')

    # def _build_trigger_list(self, trigger_dict: dict):
    #     # add all keys first
    #     for device in trigger_dict.keys():
    #         self.trigger_tree[device] = self.device_list[device]
    #     # add values, if value is a dict, recursively start over
    #     for device, subdevice in trigger_dict.items():
    #         if isinstance(subdevice, dict):
    #             self._build_trigger_list(subdevice)
    #         else:
    #             if subdevice != None:
    #                 self.trigger_tree[subdevice] = self.device_list[subdevice]
    #
    # def _verify_triggers(self):
    #
    #     # load the trigger dict
    #     if self.config['instrument']['triggers']:
    #         self.log.info('triggers found. building the trigger tree.')
    #         trigger_list = self.config['instrument']['triggers']
    #         # check that there is only one key i.e. one master device...
    #         if len(trigger_list.keys()) > 1:
    #             raise ValueError(f'more than one master trigger device. check yaml files.')
    #         # build a flat list of devices starting from the master device
    #         self.trigger_tree = dict()
    #         self._build_trigger_list(trigger_list)
    #         self.acquisition_trigger_order = list()
    #         for device in self.trigger_tree:
    #             # check that all trigger devices are valid
    #             if device not in self.device_list.keys():
    #                 raise ValueError(f'{device} is not a defined device. check yaml files.')
    #         # reverse the order so the master device is last
    #         self.trigger_tree = dict(reversed(list(self.trigger_tree.items())))
    #     else:
    #         raise ValueError(f'trigger tree is not a defined device. check yaml files.')
    #
    # TODO. figure out which task is the master task if DAQ.
    # if list(self.trigger_tree.values())[-1] == 'daqs':
    #     daq_name = list(self.trigger_tree.keys())[-1]
    #     master_task_dict = dict()
    #     for task in self.config['instrument']['devices']['daqs'][daq_name]['tasks']:
    #         print(task)
    #         # the master device will not have triggering enabled
    #         trigger_mode = self.config['instrument']['devices']['daqs'][daq_name]['tasks'][task]['timing']['trigger_mode']
    #         if trigger_mode == 'off':
    #             self.trigger_tree[daq_name]['task'] = self.config['instrument']['devices']['daqs'][daq_name]['tasks'][task]['name']
    #             master_task_dict[device['tasks'][task]['name']] = trigger_mode
    #     if len(master_task_dict.keys()) > 1:
    #         raise ValueError(f'there can only be one master task. but {master_task_dict} are all master tasks.')