from pathlib import Path
from spim_core.config_base import Config

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_simulated.yaml")
config = Config(str(config_path))

# ugly constructor and init for config values...

# loop over all filterwheels in config
filter_wheels=list()

for filter_wheel in config.cfg['devices']['filter wheels']:
	# grab config values for creating object
	driver = filter_wheel['driver']
	port = filter_wheel['port']
	filter_wheel_id = filter_wheel['id']
	filter_list = filter_wheel['filters']
	exec(f"import {driver}")
	exec(f"filter_wheels.append({driver}.FilterWheel(filter_list))")

filter_wheels[-1].set_filter('BP405')
print(filter_wheels[-1].get_filter())
filter_wheels[-1].set_filter('BP488')
print(filter_wheels[-1].get_filter())