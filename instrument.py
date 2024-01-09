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
        self.lasers = {}
        self.combiners = {}

    def load_device(self, driver: str, module: str, kwds):
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
        for key, value in settings.items():
            setattr(device, key, value)

    def construct_cameras(self, cameras_list: list):
        for camera in cameras_list:
            name = camera['name']
            self.log.info(f'constructing {name}')
            driver = camera['driver']
            module = camera['module']
            init = camera.get('init', {})
            camera_object = self.load_device(driver, module, init)
            settings = camera.get('settings', {})
            self.setup_device(camera_object, settings)

            writer = camera['writer']
            writer_object = self.load_device(writer['driver'], writer['module'], dict())
            settings = writer.get('settings', {})
            self.setup_device(writer_object, settings)

            self.cameras[name] = {
                'object': camera_object,
                'driver': driver,
                'module': module,
                'writer': {
                    'object': writer_object,
                    'driver': writer['driver'],
                    'module': writer['module']
                }
            }
    def construct_stages(self, stages_list:list):

        for stage in stages_list:
            name = stage['name']
            self.log.info(f'constructing {name}')
            driver = stage['driver']
            module = stage['module']
            init = stage['init']
            try:
                port = stage['port']
                if 'tigerasi.tiger_controller' in sys.modules.keys():
                    self.log.warning(f'tigerasi already exists')
                    init = dict(init)
                    init['tigerbox'] = self.tigerbox
                else:
                    self.log.info('loading tigerasi')
                    from tigerasi.tiger_controller import TigerController
                    self.tigerbox = TigerController(port)
                    init = dict(init)
                    init['tigerbox'] = self.tigerbox
            except:
                self.log.info('simulated tiling stage')
            stage_object = self.load_device(driver, module, init)

            settings = stage.get('settings', {})
            self.setup_device(stage_object, settings)
            if 'scanning' in stage['type']:
                self.scanning_stages[name] = {
                    'object': stage_object,
                    'driver': driver,
                    'module': module,
                }
            elif 'tiling' in stage['type']:
                self.tiling_stages[name] = {
                    'object': stage_object,
                    'driver': driver,
                    'module': module,
                }

    def construct_filter_wheels(self, filter_wheels_list: list):
        for filter_wheel in filter_wheels_list:
            name = filter_wheel['name']
            self.log.info(f'constructing {name}')
            driver = filter_wheel['driver']
            module = filter_wheel['module']
            init = filter_wheel['init']
            try:
                port = filter_wheel['port']
                if 'tigerasi.tiger_controller' in sys.modules.keys():
                    self.log.warning(f'tigerasi already exists')
                    init = dict(init)
                    init['tigerbox'] = self.tigerbox
                else:
                    self.log.info('loading tigerasi')
                    from tigerasi.tiger_controller import TigerController
                    tigerbox = TigerController(port)
                    init = dict(init)
                    init['tigerbox'] = self.tigerbox
            except:
                self.log.info('simulated filter wheel')
            filter_wheel_object = self.load_device(driver, module, init)
            try:
                settings = filter_wheel['settings']
            except:
                settings = dict()
                self.log.debug(f'no settings listed')
            self.setup_device(filter_wheel_object, settings)
            self.filter_wheels[name] = {
                'object': filter_wheel_object,
                'driver': driver,
                'module': module,
            }

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
            self.daqs[id] = {
                'object': daq_object,
                'name': name,
                'driver': driver,
                'module': module,
            }

    def construct_lasers(self, laser_list: list):

        for laser in laser_list:
            name = laser['name']
            self.log.info(f'constructing {name}')
            driver = laser['driver']
            module = laser['module']
            init = laser.get('init', {})
            settings = laser.get('settings', {})
            laser_object = self.load_device(driver, module, init)
            self.setup_device(laser_object, settings)
            self.lasers[name] = {
                'object': laser_object,
                'driver': driver,
                'module': module,
                                }
    def construct_combiners(self, combiner_list: list):

        for combiner in combiner_list:
            name = combiner['name']
            self.log.info(f'constructing {name}')
            driver = combiner['driver']
            module = combiner['module']
            init = combiner.get('init', {})
            settings = combiner.get('settings', {})
            combiner_object = self.load_device(driver, module, init)
            self.setup_device(combiner_object, settings)
            self.combiners[name] = {
                'object': combiner_object,
                'driver': driver,
                'module': module,
            }

            # setup lasers under combiner
            combiner_lasers = combiner.get('combiner_lasers', []).copy()  # TODO: Check if copy needed to not edit yaml

            for laser in combiner_lasers:
                laser['init'] = {**laser['init'], 'port': combiner_object.ser}
            # construct lasers with combiner port added
            self.construct_lasers(combiner_lasers)

    def construct(self):
        self.log.info(f'constructing instrument from {self.config_path}')
        for device in self.config.cfg['instrument']['devices'].items():
            print(device)
            device_type = device[0]
            device_list = device[1]
            construct_function = getattr(self, f'construct_{device_type}')
            construct_function(device_list)
        print(self.scanning_stages)
        print(self.tiling_stages)
        print(self.daqs)
        print(self.lasers)
        print(self.filter_wheels)
        print(self.combiners)
            # if device_type == 'cameras':
            #     cameras_list = device[1]
            #     self.construct_cameras(cameras_list)
            # if device_type == 'stages':
            #     for stage_type in device[1]:
            #         if stage_type == 'tiling':
            #             tiling_stages_list = device[1][stage_type]
            #             self.construct_tiling_stages(tiling_stages_list)
            #         elif stage_type == 'scanning':
            #             scanning_stages_list = device[1][stage_type]
            #             self.construct_scanning_stages(scanning_stages_list)
            # if device_type == 'filter_wheels':
            #     filter_wheels_list = device[1]
            #     self.construct_filter_wheels(filter_wheels_list)
            # if device_type == 'daqs':
            #     daqs_list = device[1]
            #     self.construct_daqs(daqs_list)
            # if device_type == 'lasers':
            #     laser_list = device[1]
            #     self.construct_lasers(laser_list)

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
