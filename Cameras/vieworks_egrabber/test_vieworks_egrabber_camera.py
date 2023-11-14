from pathlib import Path
from spim_core.spim_core.config_base import Config
from Cameras.vieworks_egrabber.camera_vieworks_egrabber import CameraVieworkseGrabber


this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test.yaml")
config = Config(str(config_path))

camera = CameraVieworkseGrabber(config)

print(camera.mainboard_temperature_c)
print(camera.line_interval_us)
print(camera.binning)
camera.roi = (8192, 5320)
camera.prepare(8)