driver = 'pco'
camera_id = '61009303'
# create camera object
exec(f"from voxel.devices.camera import {driver}")
exec(f"camera = ({driver}.Camera('{camera_id}'))")
# init values from _config
camera.roi = {
    'roi_width_px': camera['region of interest']['roi_width_px'],
    'roi_height_px': camera['region of interest']['roi_height_px']
}
camera.exposure_time_ms = camera['exposure_time_ms']
camera.pixel_type = camera['bit_depth']
camera.trigger = {
    'mode': camera['trigger']['mode'],
    'source': camera['trigger']['source'],
    'polarity': camera['trigger']['polarity']
}

frames = 100
camera.prepare()
camera.start()

for i in range(frames):
    camera.grab_frame()
    print(camera.acquisition_state())

camera.log_metadata()
camera.stop()
camera.close()