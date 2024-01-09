import logging
import shutil
import datetime
import subprocess
import os
import sys
import ruamel
from pathlib import Path
from spim_core.config_base import Config
import inspect
import importlib
from serial import Serial

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
        self.lasers = {}
        self.combiners = {}
        self.construct()

    def load_device(self, driver: str, module: str, kwds):
        """Load in device based on config. Expecting driver, module, and kwds input"""
        #self.log.info(f'loading {driver}.{module}')
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
        #self.log.info(f'setting up {device}')
        # successively iterate through settings keys
        for key, value in settings.items():
            setattr(device, key, value)

    def construct_device(self, device_type, device_list):

        for device in device_list:
            name = device['name']
            #self.log.info(f'constructing {name}')
            driver = device['driver']
            module = device['module']
            init = device.get('init', {})
            device_object = self.load_device(driver, module, init)
            settings = device.get('settings', {})
            self.setup_device(device_object, settings)
            device_dict = getattr(self, device_type)
            device_dict[name] = device_object

            # Add subdevices under device and fill in any needed keywords to init like
            for subdevice_type, subdevice_list in device.get('subdevices', {}).items():
                for subdevice in subdevice_list:
                    subdevice_class = getattr(importlib.import_module(subdevice['driver']), subdevice['module'])
                    subdevice_needs = inspect.signature(subdevice_class.__init__).parameters
                    for name, parameter in subdevice_needs.items():
                        if parameter.annotation == Serial and Serial in device_object.__dict__.values():
                            device_port_name = [k for k, v in device_object.__dict__.items() if v == Serial]
                            subdevice['init'][name] = getattr(device_object, *device_port_name)
                        elif parameter.annotation == type(device_object):
                            subdevice['init'][name] = device_object
                self.construct_device(subdevice_type, subdevice_list)

    # def construct_cameras(self, cameras_list: list):
    #     for camera in cameras_list:
    #         name = camera['name']
    #         self.log.info(f'constructing {name}')
    #         driver = camera['driver']
    #         module = camera['module']
    #         init = camera.get('init', {})
    #         camera_object = self.load_device(driver, module, init)
    #         settings = camera.get('settings', {})
    #         self.setup_device(camera_object, settings)
    #
    #         self.cameras[name] = camera_object
    #
    # def construct_stages(self, stages_list: list):
    #     for stage in stages_list:
    #         name = stage['name']
    #         self.log.info(f'constructing {name}')
    #         driver = stage['driver']
    #         module = stage['module']
    #         init = stage.get('init', {})
    #         stage_object = self.load_device(driver, module, init)
    #         settings = stage.get('settings', {})
    #         self.setup_device(stage_object, settings)
    #
    #         if 'tiling' in stage['type']:
    #             self.tiling_stages[name] = stage_object
    #         elif 'scanning' in stage['type']:
    #             self.scanning_stages[name] = stage_object
    #
    # def construct_filter_wheels(self, filter_wheels_list: list):
    #     for filter_wheel in filter_wheels_list:
    #         name = filter_wheel['name']
    #         self.log.info(f'constructing {name}')
    #         driver = filter_wheel['driver']
    #         module = filter_wheel['module']
    #         init = filter_wheel.get('init', {})
    #         filter_wheel_object = self.load_device(driver, module, init)
    #         settings = filter_wheel.get('settings', {})
    #         self.setup_device(filter_wheel_object, settings)
    #         self.filter_wheels[name] = filter_wheel_object
    #
    # def construct_daqs(self, daqs_list: list):
    #     for daq in daqs_list:
    #         name = daq['name']
    #         self.log.info(f'constructing {name}')
    #         driver = daq['driver']
    #         module = daq['module']
    #         init = daq['init']
    #         id = init['dev']
    #         daq_object = self.load_device(driver, module, init)
    #         ao_task = daq['tasks']['ao_task']
    #         do_task = daq['tasks']['do_task']
    #         co_task = daq['tasks']['co_task']
    #         daq_object.add_ao_task(ao_task)
    #         daq_object.add_do_task(do_task)
    #         daq_object.add_co_task(co_task)
    #         self.daqs[name] = daq_object
    #
    # def construct_lasers(self, laser_list: list):
    #
    #     for laser in laser_list:
    #         name = laser['name']
    #         self.log.info(f'constructing {name}')
    #         driver = laser['driver']
    #         module = laser['module']
    #         init = laser.get('init', {})
    #         settings = laser.get('settings', {})
    #         self.lasers[name] = self.load_device(driver, module, init)
    #         self.setup_device(self.lasers[name], settings)
    #
    # def construct_combiners(self, combiner_list: list):
    #
    #     for combiner in combiner_list:
    #         name = combiner['name']
    #         self.log.info(f'constructing {name}')
    #         driver = combiner['driver']
    #         module = combiner['module']
    #         init = combiner.get('init', {})
    #         settings = combiner.get('settings', {})
    #         self.combiners[name] = self.load_device(driver, module, init)
    #         self.setup_device(self.combiners[name], settings)
    #         # setup lasers under combiner
    #         combiner_lasers = combiner.get('combiner_lasers', []).copy()  # TODO: Check if copy needed to not edit yaml
    #
    #         for laser in combiner_lasers:
    #             laser['init'] = {**laser['init'], 'port': self.combiners[name].ser}
    #         # construct lasers with combiner port added
    #         self.construct_lasers(combiner_lasers)

    def construct(self):
        self.log.info(f'constructing instrument from {self.config_path}')
        for device_type, device_list in self.config.cfg['instrument']['devices'].items():
            self.construct_device(device_type, device_list)
        print('scanning',self.scanning_stages)
        print('tiling',self.tiling_stages)
        print('daq', self.daqs)
        print('laser', self.lasers)
        print('fw', self.filter_wheels)
        print('combiner', self.combiners)
        print('camera', self.cameras)
    # def run(self)
    # import writer and assert only one
    # assert len(writer_cfg) == 1
    # # grab config values for creating object
    # writer = writer_cfg[0]
    # driver = writer['driver']
    # exec(f"import writers.{driver}  as {driver}")
    # if driver == 'imaris':
    #     exec(f"from writers.data_structures.shared_double_buffer import SharedDoubleBuffer")
    # exec(f"data_writer = {driver}.Writer()")

    # instrument = dict()
    # instrument['cameras'] = cameras
    # instrument['tiling_stages'] = tiling_stages
    # instrument['scanning_stage'] = scanning_stage
    # instrument['filter_wheels'] = filter_wheels
    # instrument['data_writer'] = data_writer

    # # run imaris test
    # chunk_size = 64
    # frames = 128
    # instrument['data_writer'].row_count = camera_cfg[0]['region_of_interest']['height_px']
    # instrument['data_writer'].column_count = camera_cfg[0]['region_of_interest']['width_px']
    # instrument['data_writer'].frame_count = frames
    # instrument['data_writer'].chunk_count = chunk_size
    # instrument['data_writer'].x_pos = 0
    # instrument['data_writer'].y_pos = 0
    # instrument['data_writer'].z_pos = 0
    # instrument['data_writer'].x_voxel_size = 0.748
    # instrument['data_writer'].y_voxel_size = 0.748
    # instrument['data_writer'].z_voxel_size = 1
    # instrument['data_writer'].compression = writer_cfg[0]['compression']
    # instrument['data_writer'].dtype = writer_cfg[0]['data_type']
    # instrument['data_writer'].path = writer_cfg[0]['path']
    # instrument['data_writer'].filename = 'test.ims'
    # instrument['data_writer'].channel = '488'
    # instrument['data_writer'].color = writer_cfg[0]['hex_color']

    # chunk_lock = threading.Lock()

    # mem_shape = (chunk_size,
    #              camera_cfg[0]['region_of_interest']['height_px'],
    #              camera_cfg[0]['region_of_interest']['width_px'])

    # img_buffer = SharedDoubleBuffer(mem_shape,
    #                                 dtype=writer_cfg[0]['data_type'])

    # frame_index = 0
    # chunk_count = math.ceil(frames / chunk_size)
    # remainder = frames % chunk_size
    # last_chunk_size = chunk_size if not remainder else remainder
    # last_frame_index = frames - 1

    # # set up writer and camera
    # instrument['data_writer'].prepare()
    # instrument['cameras'][0].prepare()
    # instrument['data_writer'].start()
    # instrument['cameras'][0].start(frames)

    # # Images arrive serialized in repeating channel order.
    # for stack_index in range(frames):
    #     chunk_index = stack_index % chunk_size
    #     # Start a batch of pulses to generate more frames and movements.
    #     if chunk_index == 0:
    #         chunks_filled = math.floor(stack_index / chunk_size)
    #         remaining_chunks = chunk_count - chunks_filled
    #     # Grab camera frame
    #     img_buffer.write_buf[chunk_index] = \
    #         instrument['cameras'][0].grab_frame()
    #     print(instrument['cameras'][0].get_camera_acquisition_state())

    #     frame_index += 1
    #     # Dispatch either a full chunk of frames or the last chunk,
    #     # which may not be a multiple of the chunk size.
    #     if chunk_index == chunk_size - 1 or stack_index == last_frame_index:
    #         while not instrument['data_writer'].done_reading.is_set():
    #             time.sleep(0.001)
    #         # Dispatch chunk to each StackWriter compression process.
    #         # Toggle double buffer to continue writing images.
    #         # To read the new data, the StackWriter needs the name of
    #         # the current read memory location and a trigger to start.
    #         # Lock out the buffer before toggling it such that we
    #         # don't provide an image from a place that hasn't been
    #         # written yet.
    #         with chunk_lock:
    #             img_buffer.toggle_buffers()
    #             if writer_cfg[0]['path'] is not None:
    #                 instrument['data_writer'].shm_name = \
    #                     img_buffer.read_buf_mem_name
    #                 instrument['data_writer'].done_reading.clear()

    # instrument['data_writer'].wait_to_finish()
    # instrument['data_writer'].close()
    # instrument['cameras'][0].stop()
    # instrument['cameras'][0].log_metadata()

    # def run(self, overwrite: bool = False):
    #     """Collect data according to config; populate dest folder with data.

    #     :param overwrite: bool indicating if we want to overwrite any existing
    #         data if the output folder already exists. False by default.
    #     """
    #     self.cfg.sanity_check()
    #     # Define img & derivative storage folders if external folder is specified.
    #     # if external storage directory is not specified, ignore overwrite
    #     # checks and leave it undefined. Data will be written to local storage
    #     # folder.
    #     date_time_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    #     # Assume self.cfg.local_storage_dir exists if we passed sanity check.
    #     top_folder_name = Path(self.cfg.subject_id + "-ID_" + date_time_string)
    #     # Create required local folder structure.
    #     local_storage_dir = self.cfg.local_storage_dir / top_folder_name
    #     if local_storage_dir.exists() and not overwrite:
    #         self.log.error(f"Local folder {local_storage_dir.absolute()} exists. "
    #                        "This function must be rerun with overwrite=True.")
    #         raise
    #     # Create cache subfolder.
    #     self.cache_storage_dir = local_storage_dir / Path("micr/") if not self.cfg.design_specs.get('instrument_type', False) \
    #         else local_storage_dir / Path(f"{self.cfg.design_specs['instrument_type']}/")
    #     self.log.info(f"Creating cache dataset folder in: "
    #                   f"{self.cache_storage_dir.absolute()}")
    #     # Create required external folder structure.
    #     output_dir = None
    #     if self.cfg.ext_storage_dir is None:
    #         output_dir = local_storage_dir
    #     elif self.cfg.local_storage_dir == self.cfg.ext_storage_dir:
    #         output_dir = local_storage_dir
    #     else:
    #         # Only make local storage if different then external drive
    #         self.cache_storage_dir.mkdir(parents=True, exist_ok=overwrite)
    #         output_dir = self.cfg.ext_storage_dir / top_folder_name
    #         if output_dir.exists() and not overwrite:

    #             self.log.error(f"Output folder {output_dir.absolute()} exists. "
    #                            "This function must be rerun with overwrite=True.")
    #             raise
    #     self.log.info(f"Creating dataset folder in: {output_dir.absolute()}")
    #     self.img_storage_dir = output_dir / Path("micr/") if not self.cfg.design_specs.get('instrument_type', False) \
    #         else output_dir / Path(f"{self.cfg.design_specs['instrument_type']}/")
    #     self.deriv_storage_dir = output_dir / Path("derivatives/")
    #     self.img_storage_dir.mkdir(parents=True, exist_ok=overwrite)
    #     self.deriv_storage_dir.mkdir(parents=True, exist_ok=overwrite)
    #     # Save the config file we will run to the destination directory.
    #     self.cfg.save(output_dir, overwrite=overwrite)

    #     # Log to a file for the duration of this function's execution.
    #     # TODO: names should be constants.
    #     imaging_log_filepath = Path("imaging_log.log")
    #     schema_log_filepath = Path("schema_log.log")
    #     try:
    #         with self.log_to_file(imaging_log_filepath):
    #             # Create log file from which to generate the AIND schema.
    #             with self.log_to_file(schema_log_filepath, None,
    #                                   DictFormatter, AINDSchemaFilter):
    #                 self.log_git_hashes()
    #                 self.run_from_config()
    #     finally:  # Transfer log file to output folder, even on failure.
    #         # Bail early if file does not need to be transferred.
    #         if output_dir in [Path("."), None]:
    #             return
    #         # Note: shutil can't overwrite, so we must delete any prior imaging
    #         #   log in the destination folder if we are overwriting.
    #         imaging_log_dest = output_dir/Path(imaging_log_filepath.name)
    #         if overwrite and imaging_log_dest.exists():
    #             imaging_log_dest.unlink()
    #         schema_log_dest = output_dir/Path(schema_log_filepath.name)
    #         if overwrite and schema_log_dest.exists():
    #             schema_log_dest.unlink()
    #         # We must use shutil because we may be moving files across disks.
    #         shutil.move(str(imaging_log_filepath), str(output_dir))
    #         shutil.move(str(schema_log_filepath), str(output_dir))
