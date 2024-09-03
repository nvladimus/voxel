from pathlib import Path
from ruamel.yaml import YAML

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_camera_vieworks_egrabber.yaml")
config = YAML().load(Path(config_path))

# ugly constructor and init for _config values...

# loop over all cameras in _config
cameras=list()

for camera in config['devices']['cameras']:
	# grab _config values for creating object
	driver = camera['driver']
	camera_id = camera['id']
	# create camera object
	exec(f"from voxel.devices.camera import {driver}")
	exec(f"cameras.append({driver}.Camera('{camera_id}'))")
	# init values from _config
	cameras[-1].roi = {
		'roi_width_px': camera['region of interest']['roi_width_px'],
		'roi_height_px': camera['region of interest']['roi_height_px']
	}
	cameras[-1].exposure_time_ms = camera['timing']['exposure_time_ms']
	cameras[-1].pixel_type = camera['image format']['bit_depth']
	cameras[-1].bit_packing_mode = camera['image format']['bit_packing_mode']
	cameras[-1].trigger = {
		'mode': camera['trigger']['mode'],
		'source': camera['trigger']['source'],
		'polarity': camera['trigger']['polarity']
	}

cameras[-1].roi = {
	'roi_width_px': 14192,
	'roi_height_px': 10640
}

cameras[-1].binning = 1

frames = 10
cameras[-1].prepare()
cameras[-1].start()

for i in range(frames):
	cameras[-1].grab_frame()
	print(cameras[-1].acquisition_state())

cameras[-1].stop()

cameras[-1].reset()
print(cameras[-1].pixel_type)