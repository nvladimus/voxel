from simulated import Camera
import time

camera = Camera()
camera.exposure_time_ms = 20
camera.pixel_type = 'mono16'
camera.roi = {
    'width_px': 14192,
    'height_px': 10640
}
camera.prepare()
camera.start(32)
time.sleep(2)
camera.grab_frame()
camera.grab_frame()
camera.grab_frame()
camera.grab_frame()
camera.grab_frame()
camera.grab_frame()
camera.grab_frame()
camera.grab_frame()
camera.grab_frame()
camera.grab_frame()
camera.grab_frame()
camera.grab_frame()
camera.stop()