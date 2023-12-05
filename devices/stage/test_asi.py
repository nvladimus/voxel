from pathlib import Path
from spim_core.config_base import Config
from tigerasi.tiger_controller import TigerController
from asi import Stage

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_asi.yaml")
config = Config(str(config_path))

# ugly constructor...

stages=[]

for stage in config.cfg['devices']['stages'].items():
	driver = stage[1]['driver']
	port = stage[1]['port']
	hardware_axis = stage[1]['hardware_axis']
	instrument_axis = stage[1]['instrument_axis']
	try:
		tigerbox
		exec(f"stages.append({driver}.Stage(tigerbox, hardware_axis, instrument_axis))")
	except:
		tigerbox = TigerController(port)
		exec(f"import {driver}")
		exec(f"stages.append({driver}.Stage(tigerbox, hardware_axis, instrument_axis))")

# stage 0
print('settings for stage0')
stages[0].setup_stage_scan(fast_axis_start_position = 0,
                               slow_axis_start_position = 0,
                               slow_axis_stop_position = 0,
                               frame_count = 100, frame_interval_um = 1,
                               strip_count = 1, pattern = 'raster',
                               retrace_speed_percent = 50)
print(stages[0].acceleration)
stages[0].acceleration = 100.0
print(stages[0].acceleration)
print(stages[0].position)
print(stages[0].speed)
print(stages[0].limits)
stages[0].speed = 0.25
print(stages[0].mode)
stages[0].mode = 'off'
print(stages[0].mode)
print(stages[0].joystick_mapping)
stages[0].joystick_mapping = 'joystick x'
print(stages[0].joystick_mapping)
print(stages[0].joystick_polarity)
stages[0].joystick_polarity = 'inverted'
print(stages[0].joystick_polarity)
stages[0].lock_external_user_input()
stages[0].unlock_external_user_input()
print(stages[0].is_axis_moving())
stages[0].move_absolute(0, wait = False)
print(stages[0].is_axis_moving())
print(stages[0].is_axis_moving())
print(stages[0].is_axis_moving())
print(stages[0].position)
print(stages[0].is_axis_moving())
stages[0].move_relative(1000, wait = False)
print(stages[0].is_axis_moving())
print(stages[0].is_axis_moving())
print(stages[0].is_axis_moving())
print(stages[0].position)
stages[0].zero_in_place()
print(stages[0].position)
stages[0].log_metadata()

# stage 1
print('settings for stage1')
stages[1].setup_stage_scan(fast_axis_start_position = 0,
                               slow_axis_start_position = 0,
                               slow_axis_stop_position = 0,
                               frame_count = 100, frame_interval_um = 1,
                               strip_count = 1, pattern = 'raster',
                               retrace_speed_percent = 50)
print(stages[1].acceleration)
stages[1].acceleration = 100.0
print(stages[1].acceleration)
print(stages[1].position)
print(stages[1].speed)
print(stages[1].limits)
stages[1].speed = 0.25
print(stages[1].mode)
stages[1].mode = 'off'
print(stages[1].mode)
print(stages[1].joystick_mapping)
stages[1].joystick_mapping = 'joystick y'
print(stages[1].joystick_mapping)
print(stages[1].joystick_polarity)
stages[1].joystick_polarity = 'inverted'
print(stages[1].joystick_polarity)
stages[1].lock_external_user_input()
stages[1].unlock_external_user_input()
print(stages[1].is_axis_moving())
stages[1].move_absolute(0, wait = False)
print(stages[1].is_axis_moving())
print(stages[1].is_axis_moving())
print(stages[1].is_axis_moving())
print(stages[1].position)
print(stages[1].is_axis_moving())
stages[1].move_relative(1000, wait = False)
print(stages[1].is_axis_moving())
print(stages[1].is_axis_moving())
print(stages[1].is_axis_moving())
print(stages[1].position)
stages[1].zero_in_place()
print(stages[1].position)
stages[1].log_metadata()