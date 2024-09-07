from pathlib import Path
from ruamel.yaml import YAML

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_camera_simulated.yaml")
config = YAML().load(Path(config_path))

# ugly constructor...

cameras=[]

for camera in config['devices']['cameras'].items():
    driver = camera[1]['driver']
    camera_id = camera[1]['name']
    exec(f"from voxel.devices.camera import {driver}")
    exec(f"cameras.append({driver}.Camera('{camera_id}'))")

# tests
print(f'board temperature is: {cameras[0].signal_mainboard_temperature_c}')
print(f'sensor temperature is: {cameras[0].signal_mainboard_temperature_c}')
print(f'binning is: {cameras[0].binning}')
cameras[0].pixel_type = "mono16"
print(f'pixel type is: {cameras[0].pixel_type}')
print(f'line time is: {cameras[0].line_interval_us}')
print(f'sensor height is: {cameras[0].sensor_height_px}')
print(f'sensor width is: {cameras[0].sensor_width_px}')
cameras[0].exposure_time_ms = 10
print(f'exposure time is: {cameras[0].exposure_time_ms}')
cameras[0].trigger = {'mode': 'off', 'source': 'external', 'polarity': 'rising'}
print(f'trigger is: {cameras[0].trigger}')
cameras[0].binning = 2
print(f'binning is: {cameras[0].binning}')
cameras[0].prepare()
cameras[0].start(10)
for frame in range(10):
    print(cameras[0].acquisition_state())
    image = cameras[0].grab_frame()
cameras[0].stop()
cameras[0].log_metadata()