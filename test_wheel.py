from pathlib import Path
from spim_core.spim_core.config_base import Config
from tigerasi.tiger_controller import TigerController
from filterwheel_asi import FilterWheelASI

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_stage.yaml")
config = Config(str(config_path))
tigerbox = TigerController(config.cfg['stage']['port'])
wheel = FilterWheelASI(tigerbox)
wheel.set_index(1)