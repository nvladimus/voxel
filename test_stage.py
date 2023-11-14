from pathlib import Path
from spim_core.spim_core.config_base import Config
from tigerasi.tiger_controller import TigerController
from stage_asi import StageASI

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_stage.yaml")
config = Config(str(config_path))
print(config.cfg)
print(config.cfg['stage']['port'])
print(config.cfg['stage']['instrument_axis'])
tigerbox = TigerController(config.cfg['stage']['port'])
stage = StageASI(config.cfg['stage'], tigerbox)
print(stage.position)

print(stage.travel_limits)
print(stage.speed)
print(stage.speed)
