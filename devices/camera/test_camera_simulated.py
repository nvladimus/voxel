from pathlib import Path
from spim_core.config_base import Config

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_camera_simulated.yaml")
config = Config(str(config_path))

# ugly constructor...

cameras=[]

for camera in config.cfg['devices']['cameras'].items():
	driver = camera[1]['driver']
	camera_id = camera[1]['id']
	exec(f"import {driver}")
	exec(f"cameras.append({driver}.Camera('{camera_id}'))")

# tests
print(f'board temperature is: {cameras[0].mainboard_temperature_c}')
print(f'sensor temperature is: {cameras[0].sensor_temperature_c}')
print(f'binning is: {cameras[0].binning}')
cameras[0].pixel_type = "Mono8"
print(f'pixel type is: {cameras[0].pixel_type}')
print(f'line time is: {cameras[0].line_interval_us}')
cameras[0].bit_packing_mode	= 'Msb'
print(f'bit packing mode is: {cameras[0].bit_packing_mode}')
print(f'sensor height is: {cameras[0].sensor_height_px}')
print(f'sensor width is: {cameras[0].sensor_width_px}')
cameras[0].exposure_time_ms	= 10
print(f'exposure time is: {cameras[0].exposure_time_ms}')
cameras[0].trigger = ['Off', 'External', 'Rising']
print(f'trigger is: {cameras[0].trigger}')
cameras[0].roi = (14192, 10640)
print(f'roi is: {cameras[0].roi}')
cameras[0].prepare()
cameras[0].start(10)
for frame in range(10):
	cameras[0].get_camera_acquisition_state()
	cameras[0].grab_frame()
cameras[0].stop()
cameras[0].log_metadata()