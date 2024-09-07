from pathlib import Path
from ruamel.yaml import YAML
import numpy
import tifffile

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_dsnu_vieworks_egrabber.yaml")
config = YAML().load(Path(config_path))

# ugly constructor and init for _config values...

camera_config = config['devices']['cameras'][0]

# grab _config values for creating object
driver = camera_config['driver']
camera_id = camera_config['id']
# create camera object
exec(f"from voxel.devices.camera import {driver}")
exec(f"camera = {driver}.Camera('{camera_id}')")
# init values from _config
camera.roi = {
	'roi_width_px': camera_config['region of interest']['roi_width_px'],
	'roi_height_px': camera_config['region of interest']['roi_height_px']
}
camera.exposure_time_ms = camera_config['timing']['exposure_time_ms']
camera.bit_packing_mode = camera_config['image format']['bit_packing_mode']
camera.trigger = {
	'mode': camera_config['trigger']['mode'],
	'source': camera_config['trigger']['source'],
	'polarity': camera_config['trigger']['polarity']
}

pixel_types = ['mono16']

for pixel_type in pixel_types:

	print(pixel_type)

	camera.pixel_type = pixel_type
	print(camera.pixel_type)

	mean_image = numpy.zeros((camera.roi['roi_height_px'], camera.roi['roi_width_px']), dtype = 'float32')
	median_image = numpy.zeros((camera.roi['roi_height_px'], camera.roi['roi_width_px']), dtype = 'float32')
	std_image = numpy.zeros((camera.roi['roi_height_px'], camera.roi['roi_width_px']), dtype = 'float32')
	max_image = numpy.zeros((camera.roi['roi_height_px'], camera.roi['roi_width_px']), dtype = 'float32')
	min_image = numpy.zeros((camera.roi['roi_height_px'], camera.roi['roi_width_px']), dtype = 'float32')

	loops = 1
	frames = 100

	for j in range(loops):
		im = numpy.zeros((frames, camera.roi['roi_height_px'], camera.roi['roi_width_px']), dtype = 'uint16')
		camera.prepare()
		camera.start()
		for i in range(frames):
			im[i] = camera.grab_frame()
			print(camera.acquisition_state())
		camera.stop()
		mean_image += numpy.mean(im, axis = 0)
		median_image += numpy.median(im, axis = 0)
		std_image += numpy.std(im, axis = 0)
		max_image += numpy.max(im, axis = 0)
		min_image += numpy.min(im, axis = 0)

	mean_image = mean_image/loops
	median_image = median_image/loops
	std_image = std_image/loops
	max_image = max_image/loops
	min_image = min_image/loops

	tifffile.imwrite(f'mean_image_{pixel_type}.tiff', mean_image.astype('float32'))
	tifffile.imwrite(f'median_image_{pixel_type}.tiff', median_image.astype('float32'))
	tifffile.imwrite(f'std_image_{pixel_type}.tiff', std_image.astype('float32'))
	tifffile.imwrite(f'max_image_{pixel_type}.tiff', max_image.astype('float32'))
	tifffile.imwrite(f'min_image_{pixel_type}.tiff', min_image.astype('float32'))

camera.close()