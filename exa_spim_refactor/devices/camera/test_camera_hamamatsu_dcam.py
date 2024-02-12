from pathlib import Path
from ruamel.yaml import YAML

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_camera_hamamatsu_dcam.yaml")
config = YAML().load(Path(config_path))

# loop over all cameras in config
cameras=list()

for camera in config['devices']['cameras']:
    # grab config values for creating object
    driver = camera['driver']
    camera_id = camera['id']
    # create camera object
    exec(f"import {driver}")
    exec(f"cameras.append({driver}.Camera('{camera_id}'))")
    # init values from config
    cameras[-1].roi = {
        'width_px': camera['region of interest']['width_px'], 
        'height_px': camera['region of interest']['height_px']
    }
    cameras[-1].exposure_time_ms = camera['exposure_time_ms']
    cameras[-1].pixel_type = camera['bit_depth']
    cameras[-1].trigger = {
        'mode': camera['trigger']['mode'],
        'source': camera['trigger']['source'],
        'polarity': camera['trigger']['polarity']
    }

frames = 100
cameras[-1].prepare()
cameras[-1].start()

for i in range(frames):
    cameras[-1].grab_frame()
    print(cameras[-1].signal_acquisition_state())

cameras[-1].log_metadata()
cameras[-1].stop()
cameras[-1].close()