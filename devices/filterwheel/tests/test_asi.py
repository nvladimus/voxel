from pathlib import Path
from spim_core.config_base import Config
from tigerasi.tiger_controller import TigerController
from asi import FilterWheel

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_asi.yaml")
config = Config(str(config_path))
print(config.cfg)
# tigerbox = TigerController(config.cfg['devices']['filterwheel']['port'])
# wheel = FilterWheelASI(tigerbox, confg.cfg['devices']['filterwheel']['id'], ['devices']['filterwheel']['filters'])
# wheel.set_index(1)