from pathlib import Path
from spim_core.spim_core.config_base import Config
from tigerasi.tiger_controller import TigerController
from stage_asi import StageASI

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_stage.yaml")
config = Config(str(config_path))
tigerbox = TigerController(config.cfg['stage']['port'])
stage = StageASI(tigerbox, config.cfg['stage']['hardware_axis'], config.cfg['stage']['instrument_axis'])
# print(stage.acceleration_ms)
# stage.acceleration_ms = 100.01
# print(stage.acceleration_ms)
# print(stage.position)
# print(stage.speed)
# print(stage.limits)
# stage.speed = 1
# print(stage.ttl)
# stage.ttl = 'on'
# print(stage.ttl)
# print(stage.joystick_mapping)
# stage.joystick_mapping = 'joystick x'
# print(stage.joystick_mapping)
# stage.joystick_polarity = 'inverted'
# stage.lock_external_user_input()
# stage.unlock_external_user_input()
# print(stage.is_moving())
# stage.move_absolute(-20000, wait = False)
# print(stage.is_moving())
# print(stage.is_moving())
# print(stage.is_moving())
# print(stage.position)
# print(stage.is_axis_moving())
# stage.move_relative_um(1000, wait = False)
# print(stage.is_axis_moving())
# print(stage.is_axis_moving())
# print(stage.is_axis_moving())
# print(stage.position_um)
# stage.zero_in_place()
# print(stage.position_um)
# stage.log_metadata()