from pathlib import Path
from ruamel.yaml import YAML

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_simulated.yaml")
config = YAML().load(Path(config_path))

# ugly constructor...

stages=[]

for stage in config['devices']['stages'].items():
    driver = stage[1]['driver']
    port = stage[1]['port']
    hardware_axis = stage[1]['hardware_axis']
    instrument_axis = stage[1]['instrument_axis']
    exec(f"from voxel.devices.stage import {driver}")
    exec(f"stages.append({driver}.Stage(hardware_axis, instrument_axis))")

# stage 0
print('settings for stage0')
stages[0].speed = 0.25
print(stages[0].speed)
stages[0].move_absolute(10, wait = True)
print(stages[0].position)