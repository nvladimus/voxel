import math
import numpy
import threading
import time
from pathlib import Path
from spim_core.config_base import Config
import sys

def load_device(driver, module, kwds):
    """Load in device based on config. Expecting driver, module, and kwds input"""
    __import__(driver)
    device_class = getattr(sys.modules[driver], module)
    for k, v in kwds.items():
        if str(v).split('.')[0] in dir(sys.modules[driver]):
            arg_class = getattr(sys.modules[driver], v.split('.')[0])
            kwds[k] = getattr(arg_class, '.'.join(v.split('.')[1:]))
    return device_class(**kwds)

def setup_device(device, driver, setup):
    """Setup device based on config
    :param device: device to be setup
    :param setup: dictionary of attributes, values to set according to config"""

    for property, value in setup.items():
        if str(value).split('.')[0] in dir(sys.modules[driver]):
            arg_class = getattr(sys.modules[driver], value.split('.')[0])
            value = getattr(arg_class, '.'.join(value.split('.')[1:]))
        else:
            value = eval(value) if '.' in str(value) else value

        setattr(device, property, value)


if __name__ == '__main__':

	this_dir = Path(__file__).parent.resolve() # directory of this test file.
	config_path = this_dir / Path("test_instrument.yaml")
	config = Config(str(config_path))
	camera_cfg = config.cfg['instrument']['devices']['cameras']
	tiling_stage_cfg = config.cfg['instrument']['devices']['stages']['tiling']
	scanning_stage_cfg = config.cfg['instrument']['devices']['stages']['scanning']
	filter_wheel_cfg = config.cfg['instrument']['devices']['filter_wheels']
	writer_cfg = config.cfg['instrument']['devices']['writers']
	laser_cfg = config.cfg['instrument']['devices']['lasers']
	# ugly constructor and init for config values...

	# loop over all cameras in config
	cameras=list()

	for camera in camera_cfg:
		# grab config values for creating object
		driver = camera['driver']
		camera_id = camera['id']
		# create camera object
		exec(f"import devices.camera.{driver} as {driver}")
		exec(f"cameras.append({driver}.Camera('{camera_id}'))")
		# init values from config
		cameras[-1].roi = (camera['region_of_interest']['width_px'], camera['region_of_interest']['height_px'])
		cameras[-1].exposure_time_ms = camera['timing']['exposure_time_ms']
		cameras[-1].pixel_type = camera['image_format']['bit_depth']
		cameras[-1].bit_packing_mode = camera['image_format']['bit_packing_mode']
		cameras[-1].trigger = (camera['trigger']['mode'], camera['trigger']['source'], camera['trigger']['polarity'])

	# loop over all tiling stages in config
	tiling_stages=dict()
	for stage in tiling_stage_cfg:
		# grab config values for creating object
		driver = stage['driver']
		port = stage['port']
		hardware_axis = stage['hardware_axis']
		instrument_axis = stage['instrument_axis']
		# create stage object, check if exists already
		if 'tigerbox' in locals() or 'tigerbox' in globals():
			exec(f"tiling_stages[instrument_axis] = {driver}.Stage(tigerbox, hardware_axis, instrument_axis)")
		else:
			from tigerasi.tiger_controller import TigerController
			tigerbox = TigerController(port)
			exec(f"import devices.stage.{driver}  as {driver}")
			exec(f"tiling_stages[instrument_axis] = {driver}.Stage(tigerbox, hardware_axis, instrument_axis)")
		# init values from config
		tiling_stages[instrument_axis].speed = stage['speed_mm_s']
		tiling_stages[instrument_axis].acceleration = stage['acceleration_ms']
		tiling_stages[instrument_axis].backlash = stage['backlash_mm']
		tiling_stages[instrument_axis].mode = stage['mode']
		tiling_stages[instrument_axis].joystick_polarity = stage['joystick_polarity']
		tiling_stages[instrument_axis].joystick_mapping = stage['joystick_mapping']

	# import scanning stage and assert only one
	assert len(scanning_stage_cfg) == 1
	# grab config values for creating object
	stage = scanning_stage_cfg[0]
	driver = stage['driver']
	port = stage['port']
	hardware_axis = stage['hardware_axis']
	instrument_axis = stage['instrument_axis']
	# create stage object, check if exists already
	if 'tigerbox' in locals() or 'tigerbox' in globals():
		exec(f"scanning_stage = {driver}.Stage(tigerbox, hardware_axis, instrument_axis)")
	else:
		from tigerasi.tiger_controller import TigerController
		tigerbox = TigerController(port)
		exec(f"import devices.stage.{driver}  as {driver}")
		exec(f"scanning_stage = {driver}.Stage(tigerbox, hardware_axis, instrument_axis)")
	# init values from config
	scanning_stage.speed = stage['speed_mm_s']
	scanning_stage.acceleration = stage['acceleration_ms']
	scanning_stage.backlash = stage['backlash_mm']
	scanning_stage.mode = stage['mode']
	scanning_stage.joystick_polarity = stage['joystick_polarity']
	scanning_stage.joystick_mapping = stage['joystick_mapping']

	# loop over all filterwheels in config
	filter_wheels=list()

	for filter_wheel in filter_wheel_cfg:
		# grab config values for creating object
		driver = filter_wheel['driver']
		port = filter_wheel['port']
		filter_wheel_id = filter_wheel['id']
		filter_list = filter_wheel['filters']
		# create stage object, check if exists already
		if 'tigerbox' in locals() or 'tigerbox' in globals():
			try:
				exec(f"filter_wheels.append({driver}.FilterWheel(tigerbox, filter_wheel_id, filter_list))")
			except:
				exec(f"import devices.filterwheel.{driver}  as {driver}")
				exec(f"filter_wheels.append({driver}.FilterWheel(tigerbox, filter_wheel_id, filter_list))")
		else:
			from tigerasi.tiger_controller import TigerController
			tigerbox = TigerController(port)
			exec(f"import devices.filterwheel.{driver}  as {driver}")
			exec(f"filter_wheels.append({driver}.FilterWheel(tigerbox, filter_wheel_id, filter_list))")

	# import writer and assert only one
	assert len(writer_cfg) == 1
	# grab config values for creating object
	writer = writer_cfg[0]
	driver = writer['driver']
	exec(f"import writers.{driver}  as {driver}")
	if driver == 'imaris':
		exec(f"from writers.data_structures.shared_double_buffer import SharedDoubleBuffer")
	exec(f"data_writer = {driver}.Writer()")

	lasers = {}
	combiners = {}
	for name, specs in laser_cfg.items():
		if 'type' in specs.keys() and specs['type'] == 'laser':
			# If type is laser, create laser class and use kw specified
			lasers[name] = load_device(specs['driver'], specs['module'], specs['kwds'])
			setup_device(lasers[name], specs['driver'], specs['setup'])
		elif 'type' in specs.keys() and specs['type'] == 'combiner':
			# If type is combiner, set up combiner then set up all lasers inside combiner
			combiners[name] = load_device(specs['driver'], specs['module'], specs['kwds'])
			setup_device(combiners[name], specs['driver'], specs['setup'])
			for nm in specs.keys():
				if nm.isdigit() and specs[nm]['type'] == 'laser':
					kwds = dict(specs[nm]['kwds'])
					kwds['port'] = combiners[name]  # Add combiner port to kwds
					lasers[nm] = load_device(specs[nm]['driver'], specs[nm]['module'], kwds)
					setup_device(lasers[nm], specs[nm]['driver'], specs[nm]['setup'])


	instrument = dict()
	instrument['cameras'] = cameras
	instrument['tiling_stages'] = tiling_stages
	instrument['scanning_stage'] = scanning_stage
	instrument['filter_wheels'] = filter_wheels
	instrument['data_writer'] = data_writer
	instrument['lasers'] = lasers
	instrument['combiners'] = combiners

	# run imaris test
	chunk_size = 64
	frames = 128
	instrument['data_writer'].row_count = camera_cfg[0]['region_of_interest']['height_px']
	instrument['data_writer'].column_count = camera_cfg[0]['region_of_interest']['width_px']
	instrument['data_writer'].frame_count = frames
	instrument['data_writer'].chunk_count = chunk_size
	instrument['data_writer'].x_pos = 0
	instrument['data_writer'].y_pos = 0
	instrument['data_writer'].z_pos = 0
	instrument['data_writer'].x_voxel_size = 0.748
	instrument['data_writer'].y_voxel_size = 0.748
	instrument['data_writer'].z_voxel_size = 1
	instrument['data_writer'].compression = writer_cfg[0]['compression']
	instrument['data_writer'].dtype = writer_cfg[0]['data_type']
	instrument['data_writer'].path = writer_cfg[0]['path']
	instrument['data_writer'].filename = 'test.ims'
	instrument['data_writer'].channel = '488'
	instrument['data_writer'].color = writer_cfg[0]['hex_color']

	chunk_lock = threading.Lock()

	mem_shape = (chunk_size,
	             camera_cfg[0]['region_of_interest']['height_px'],
	             camera_cfg[0]['region_of_interest']['width_px'])

	img_buffer = SharedDoubleBuffer(mem_shape,
	                                dtype=writer_cfg[0]['data_type'])

	frame_index = 0
	chunk_count = math.ceil(frames / chunk_size)
	remainder = frames % chunk_size
	last_chunk_size = chunk_size if not remainder else remainder
	last_frame_index = frames - 1

	# set up writer and camera
	instrument['data_writer'].prepare()
	instrument['cameras'][0].prepare()
	instrument['data_writer'].start()
	instrument['cameras'][0].start(frames)

	# Images arrive serialized in repeating channel order.
	for stack_index in range(frames):
	    chunk_index = stack_index % chunk_size
	    # Start a batch of pulses to generate more frames and movements.
	    if chunk_index == 0:
	        chunks_filled = math.floor(stack_index / chunk_size)
	        remaining_chunks = chunk_count - chunks_filled
	    # Grab camera frame
	    img_buffer.write_buf[chunk_index] = \
	    	instrument['cameras'][0].grab_frame()
	    print(instrument['cameras'][0].get_camera_acquisition_state())

	    frame_index += 1
	    # Dispatch either a full chunk of frames or the last chunk,
	    # which may not be a multiple of the chunk size.
	    if chunk_index == chunk_size - 1 or stack_index == last_frame_index:
	        while not instrument['data_writer'].done_reading.is_set():
	            time.sleep(0.001)
	        # Dispatch chunk to each StackWriter compression process.
	        # Toggle double buffer to continue writing images.
	        # To read the new data, the StackWriter needs the name of
	        # the current read memory location and a trigger to start.
	        # Lock out the buffer before toggling it such that we
	        # don't provide an image from a place that hasn't been
	        # written yet.
	        with chunk_lock:
	            img_buffer.toggle_buffers()
	            if writer_cfg[0]['path'] is not None:
	                instrument['data_writer'].shm_name = \
	                    img_buffer.read_buf_mem_name
	                instrument['data_writer'].done_reading.clear()

	instrument['data_writer'].wait_to_finish()
	instrument['data_writer'].close()
	instrument['cameras'][0].stop()
	instrument['cameras'][0].log_metadata()
