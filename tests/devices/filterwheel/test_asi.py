from pathlib import Path
from tigerasi.tiger_controller import TigerController
from ruamel.yaml import YAML

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_asi.yaml")
config = YAML().load(Path(config_path))

# ugly constructor and init for _config values...

# loop over all filterwheels in _config
filter_wheels=list()

for filter_wheel in config['devices']['filter wheels']:
    # grab _config values for creating object
    driver = filter_wheel['driver']
    port = filter_wheel['port']
    filter_wheel_id = filter_wheel['id']
    filter_list = filter_wheel['filters']
    exec(f"from voxel.devices.filterwheel import {driver}")
    exec(f"filter_wheels.append({driver}.FilterWheel(port, filter_wheel_id, filter_list))")

filter_wheels[-1].filter = 'BP405'
print(filter_wheels[-1].filter)
filter_wheels[-1].filter = 'BP488'
print(filter_wheels[-1].filter)