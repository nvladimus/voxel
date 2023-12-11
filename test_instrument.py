from pathlib import Path
from spim_core.config_base import Config

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_instrument.yaml")
config = Config(str(config_path))

# ugly constructor and init for config values...

# loop over all cameras in config
cameras=list()

for camera in config.cfg['instrument']['devices']['cameras']:
	# grab config values for creating object
	driver = camera['driver']
	camera_id = camera['id']
	# create camera object
	exec(f"import devices.camera.{driver} as {driver}")
	exec(f"cameras.append({driver}.Camera('{camera_id}'))")
	# init values from config
	camera.roi = (camera['region of interest']['width_px'], camera['region of interest']['height_px'])
	camera.exposure_time_ms = camera['timing']['exposure_time_ms']
	camera.pixel_type = camera['image format']['bit_depth']
	camera.bit_packing_mode = camera['image format']['bit_packing_mode']
	camera.trigger = (camera['trigger']['mode'], camera['trigger']['source'], camera['trigger']['polarity'])

# loop over all tiling stages in config
tiling_stages=dict()
for stage in config.cfg['instrument']['devices']['stages']['tiling']:
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
assert len(config.cfg['instrument']['devices']['stages']['scanning']) == 1
# grab config values for creating object
stage = config.cfg['instrument']['devices']['stages']['scanning'][0]
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

for filter_wheel in config.cfg['instrument']['devices']['filter wheels']:
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
assert len(config.cfg['instrument']['devices']['writers']) == 1
# grab config values for creating object
writer = config.cfg['instrument']['devices']['writers'][0]
compressor_style = writer['compression']
data_type = writer['data_type']
local_storage_dir = writer['path']
stack_file_name = 'test'
channel = '488'
hex_color = config.cfg['writer']['hex_color']
stack_file_name = "test_imaris.ims"



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

instrument = dict()
instrument['cameras'] = cameras
instrument['tiling_stages'] = tiling_stages
instrument['scanning_stage'] = scanning_stage
instrument['filter_wheels'] = filter_wheels

print(instrument)
print(instrument['cameras'])
print(instrument['tiling_stages'])
print(instrument['scanning_stage'])
print(instrument['filter_wheels'])
