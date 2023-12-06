import logging
import numpy
import time
from base import BaseCamera

# constants for VP-151MX camera

MIN_WIDTH_PX = 64    
MAX_WIDTH_PX = 14192
DIVISIBLE_WIDTH_PX = 16
MIN_HEIGHT_PX = 2
MAX_HEIGHT_PX = 10640
DIVISIBLE_HEIGHT_PX = 1
MIN_EXPOSURE_TIME_MS = 0.001
MAX_EXPOSURE_TIME_MS = 6e4

PIXEL_TYPES = {
    "Mono8":  "uint8",
    "Mono16": "uint16"
}

LINE_INTERVALS_US = {
    "Mono8":  15.00,
    "Mono16": 45.44
}

class Camera(BaseCamera):

    def __init__(self, camera_id):

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.simulated_pixel_type = None
        self.simulated_line_interval_us = None
        self.simulated_exposure_time_ms = None
        self.simulated_width_px = None
        self.simulated_height_px = None
        self.simulated_width_offset_px = None
        self.simulated_height_offset_px = None

    @property
    def exposure_time_ms(self):
        return self.simulated_exposure_time_ms

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float):

        if exposure_time_ms < MIN_EXPOSURE_TIME_MS or \
           exposure_time_ms > MAX_EXPOSURE_TIME_MS:
            self.log.error(f"exposure time must be >{MIN_EXPOSURE_TIME_MS} ms \
                             and <{MAX_EXPOSURE_TIME_MS} ms")
            raise ValueError(f"exposure time must be >{MIN_EXPOSURE_TIME_MS} ms \
                             and <{MAX_EXPOSURE_TIME_MS} ms")

        # Note: round ms to nearest us
        self.simulated_exposure_time_ms = exposure_time_ms
        self.log.info(f"exposure time set to: {exposure_time_ms} ms")

    @property
    def roi(self):
        return {'width_px': self.simulated_width_px,
                'height_px': self.simulated_height_px,
                'width_offset_px': self.simulated_width_offset_px,
                'height_offest_px': self.simulated_height_offset_px}

    @roi.setter
    def roi(self, value: tuple):

        width_px, height_px = value

        sensor_height_px = MAX_HEIGHT_PX
        sensor_width_px = MAX_WIDTH_PX

        if height_px < MIN_WIDTH_PX or \
           (height_px % DIVISIBLE_HEIGHT_PX) != 0 or \
           height_px > MAX_HEIGHT_PX:
            self.log.error(f"Height must be >{MIN_HEIGHT_PX} px, \
                             <{MAX_HEIGHT_PX} px, \
                             and a multiple of {DIVISIBLE_HEIGHT_PX} px!")
            raise ValueError(f"Height must be >{MIN_HEIGHT_PX} px, \
                             <{MAX_HEIGHT_PX} px, \
                             and a multiple of {DIVISIBLE_HEIGHT_PX} px!")

        if width_px < MIN_WIDTH_PX or \
           (width_px % DIVISIBLE_WIDTH_PX) != 0 or \
           width_px > MAX_WIDTH_PX:
            self.log.error(f"Width must be >{MIN_WIDTH_PX} px, \
                             <{MAX_WIDTH_PX}, \
                            and a multiple of {DIVISIBLE_WIDTH_PX} px!")
            raise ValueError(f"Width must be >{MIN_WIDTH_PX} px, \
                             <{MAX_WIDTH_PX}, \
                            and a multiple of {DIVISIBLE_WIDTH_PX} px!")

        # width offset must be a multiple of the divisible width in px
        centered_width_offset_px = round((sensor_width_px/2 - width_px/2)/DIVISIBLE_WIDTH_PX)*DIVISIBLE_WIDTH_PX  
        # Height offset must be a multiple of the divisible height in px
        centered_height_offset_px = round((sensor_height_px/2 - height_px/2)/DIVISIBLE_HEIGHT_PX)*DIVISIBLE_HEIGHT_PX

        self.simulated_width_px = width_px
        self.simulated_height_px = height_px
        self.simulated_width_offset_px = centered_width_offset_px
        self.simulated_height_offset_px = centered_height_offset_px

    @property
    def pixel_type(self):
        pixel_type = self.simulated_pixel_type
        # invert the dictionary and find the abstracted key to output
        return next(key for key, value in PIXEL_TYPES.items() if value == pixel_type)

    @pixel_type.setter
    def pixel_type(self, pixel_type_bits: str):
        valid = list(PIXEL_TYPES.keys())
        if pixel_type_bits not in valid:
            raise ValueError("pixel_type_bits must be one of %r." % valid)
        
        self.simulated_pixel_type = PIXEL_TYPES[pixel_type_bits]
        self.log.info(f"pixel type set_to: {pixel_type_bits}")

    @property
    def line_interval_us(self):
        pixel_type = self.simulated_pixel_type
        self.simulated_line_interval_us = LINE_INTERVALS_US[self.pixel_type]
        return self.simulated_line_interval_us

    @property
    def sensor_width_px(self):
        return MAX_WIDTH_PX

    @property
    def sensor_height_px(self):
        return MAX_HEIGHT_PX

    def prepare(self, buffer_size_frames: int = 8):
        self.log.info('Simulated camera preparing...')
        pass

    def start(self, frame_count: int, live: bool = False):
        self.log.info('Simulated camera starting...')
        pass

    def stop(self):
        self.log.info('Simulated camera stopping...')
        pass

    def grab_frame(self):
        start_time = time.time()
        column_count = self.simulated_width_px
        row_count = self.simulated_height_px
        frame_time_s = (row_count*self.simulated_line_interval_us/1000+self.simulated_exposure_time_ms)/1000
        image = numpy.random.randint(low=0, high=1, size=(row_count, column_count), dtype=self.simulated_pixel_type)
        while (time.time() - start_time) < frame_time_s:
            time.sleep(0.01)
        return image