from pathlib import Path
from spim_core.config_base import Config
from tigerasi.tiger_controller import TigerController
from asi import FilterWheel

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_asi.yaml")
config = Config(str(config_path))
port = config.cfg['devices']['filterwheel'][0]['port']
filter_wheel_id = config.cfg['devices']['filterwheel'][0]['id']
filter_list = config.cfg['devices']['filterwheel'][0]['filters']

tigerbox = TigerController(port)
wheel = FilterWheel(tigerbox, filter_wheel_id, filter_list)

wheel.set_index('BP405')
print(wheel.get_index())
wheel.set_index('BP488')
print(wheel.get_index())