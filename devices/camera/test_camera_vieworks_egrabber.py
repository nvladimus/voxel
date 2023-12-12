from pathlib import Path
from spim_core.config_base import Config

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_camera_vieworks_egrabber.yaml")
config = Config(str(config_path))

# ugly constructor and init for config values...

# loop over all cameras in config
cameras=list()

for camera in config.cfg['devices']['cameras']:
	# grab config values for creating object
	driver = camera['driver']
	camera_id = camera['id']
	# create camera object
	exec(f"import {driver}")
	exec(f"cameras.append({driver}.Camera('{camera_id}'))")
	# init values from config
	cameras[-1].roi = (camera['region of interest']['width_px'], camera['region of interest']['height_px'])
	cameras[-1].exposure_time_ms = camera['timing']['exposure_time_ms']
	cameras[-1].pixel_type = camera['image format']['bit_depth']
	cameras[-1].bit_packing_mode = camera['image format']['bit_packing_mode']
	cameras[-1].trigger = (camera['trigger']['mode'], camera['trigger']['source'], camera['trigger']['polarity'])

frames = 10
cameras[-1].prepare()
cameras[-1].start(frames)

for i in range(frames):
	cameras[-1].grab_frame()
	print(cameras[-1].get_camera_acquisition_state())

cameras[-1].stop()