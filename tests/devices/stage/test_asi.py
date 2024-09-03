from pathlib import Path
from tigerasi.tiger_controller import TigerController
from ruamel.yaml import YAML

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_asi.yaml")
config = YAML().load(Path(config_path))

# ugly constructor and init for _config values...

# loop over all tiling stages in _config
tiling_stages=dict()
for stage in config['devices']['stages']['tiling']:
    # grab _config values for creating object
    driver = stage['driver']
    port = stage['port']
    hardware_axis = stage['hardware_axis']
    instrument_axis = stage['instrument_axis']
    # create stage object, check if exists already
    exec(f"from voxel.devices.stage import {driver}")
    exec(f"tiling_stages[instrument_axis] = {driver}.Stage(port, hardware_axis, instrument_axis)")
    # init values from _config
    tiling_stages[instrument_axis].speed = stage['speed_mm_s']
    tiling_stages[instrument_axis].acceleration = stage['acceleration_ms']
    tiling_stages[instrument_axis].backlash = stage['backlash_mm']
    tiling_stages[instrument_axis].mode = stage['mode']
    tiling_stages[instrument_axis].joystick_polarity = stage['joystick_polarity']
    tiling_stages[instrument_axis].joystick_mapping = stage['joystick_mapping']

# import scanning stage and assert only one
assert len(config['devices']['stages']['scanning']) == 1
# grab _config values for creating object
stage = config['devices']['stages']['scanning'][0]
driver = stage['driver']
port = stage['port']
hardware_axis = stage['hardware_axis']
instrument_axis = stage['instrument_axis']
exec(f"from voxel.devices.stage import {driver}")
exec(f"scanning_stage = {driver}.Stage(port, hardware_axis, instrument_axis)")
# init values from _config
scanning_stage.speed = stage['speed_mm_s']
scanning_stage.acceleration = stage['acceleration_ms']
scanning_stage.backlash = stage['backlash_mm']
scanning_stage.mode = stage['mode']
scanning_stage.joystick_polarity = stage['joystick_polarity']
scanning_stage.joystick_mapping = stage['joystick_mapping']