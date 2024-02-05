import logging
import numpy
import time
from .base import BaseCamera
from pco import *

BUFFER_SIZE_MB = 2400

BINNING = {
    "1x1": 1,
    "2x2": 2,
    "4x4": 4
}

# full pco trigger mappings
# "auto sequence": 0,
# "software trigger": 1,
# "external exposure start & software trigger": 2,
# "external exposure control": 3,
# "external synchronized": 4,
# "fast external exposure control": 5,
# "external CDS control": 6,
# "slow external exposure control": 7,
# "external synchronized HDSDI": 258

TRIGGERS = {
    "modes": {
        "on": 4,
        "off": 0
    },
    "sources": None
    "polarity": None
}

# full pco readout mode mappings
# * 'top bottom'
# * 'top center bottom center'
# * 'center top center bottom'
# * 'center top bottom center'
# * 'top center center bottom'

READOUT_MODES = {
    "rolling": "center top center bottom",
    "light sheet forward": "top bottom",
    "light sheet backward": "inverse"
}

class Camera(BaseCamera):

    def __init__(self, id = str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.id = id
        # note self.id here is the interface, not a unique camera id
        # potential to do -> this could be hardcoded and changed in the pco sdk
        # error handling is taken care of within pco api
        self.camera = pco.Camera(interface=self.id)

        # gather min max values
        # convert from s to ms
        self.min_exposure_time_ms = self.pco.description['min exposure time']*1e3
        self.max_exposure_time_ms = self.pco.description['max exposure time']*1e3
        self.step_exposure_time_ms = self.pco.description['min exposure step']*1e3
        self.min_width_px = self.pco.description['min width']
        self.max_width_px = self.pco.description['max width']
        self.min_height_px = self.pco.description['min height']
        self.max_height_px = self.pco.description['max height']
        self.step_width_px = self.pco.description['roi steps'][0]
        self.step_height_px = self.pco.description['roi steps'][1]

        # intialize pco camera configuration
        self.configuration = {
            'exposure time': None,
            'roi': None,
            'trigger': None,
            'acquire': None,
            'binning': None
        }

        self.lightsheet_configuration = {
            "scmos readout": None,
            "line time": None,
            "lines exposure": None,
        }

    @property
    def exposure_time_ms(self):
        # convert from s units to ms
        return self.pco.exposure_time*1000

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float):

        if exposure_time_ms < self.min_exposure_time_ms or \
                exposure_time_ms > self.max_exposure_time_ms:
            self.log.error(f"exposure time must be >{self.min_exposure_time_ms} ms \
                             and <{self.max_exposure_time_ms} ms")
            raise ValueError(f"exposure time must be >{self.min_exposure_time_ms} ms \
                             and <{self.max_exposure_time_ms} ms")

        # Note: this pco function autocalculates the timebase unit to be ms
        self.pco.exposure_time = exposure_time_ms
        self.log.info(f"exposure time set to: {exposure_time_ms} ms")

    @property
    def roi(self):
        # roi {'x0', 'y0', 'x1', 'y1'}
        roi = self.pco.sdk.get_roi()
        return {'width_px': roi['x1'] - roi['x0'],
                'height_px': roi['y1'] - roi['y0'],
                'width_offset_px': roi['x0'],
                'height_offest_px': roi['y0']}

    @roi.setter
    def roi(self, roi: dict):

        # set roi to origin {'x0', 'y0', 'x1', 'y1'}
        self.pco.sdk.set_roi(0, 0, 0, 0)

        width_px = roi['width_px']
        height_px = roi['height_px']

        sensor_height_px = self.max_height_px
        sensor_width_px = self.max_width_px

        if height_px < self.min_height_px or \
                (height_px % self.step_height_px) != 0 or \
                height_px > self.max_height_px:
            self.log.error(f"Height must be >{self.min_height_px} px, \
                             <{self.max_height_px} px, \
                             and a multiple of {self.step_height_px} px!")
            raise ValueError(f"Height must be >{self.min_height_px} px, \
                             <{self.max_height_px} px, \
                             and a multiple of {self.step_height_px} px!")

        if width_px < self.min_width_px or \
                (width_px % self.step_width_px) != 0 or \
                width_px > self.max_width_px:
            self.log.error(f"Width must be >{self.min_width_px} px, \
                             <{self.max_width_px}, \
                            and a multiple of {self.step_width_px} px!")
            raise ValueError(f"Width must be >{self.min_width_px} px, \
                             <{self.max_width_px}, \
                            and a multiple of {self.step_width_px} px!")

        self.pco.sdk.set_roi(0, 0, width_px, 0)
        # width offset must be a multiple of the divisible width in px
        centered_width_offset_px = round((sensor_width_px / 2 - width_px / 2) / self.step_width_px) * self.step_width_px
        self.pco.sdk.set_roi(centered_width_offset_px, 0, centered_width_offset_px+width_px, 0)
        self.pco.sdk.set_roi(centered_width_offset_px, 0, centered_width_offset_px+width_px, height_px)
        # Height offset must be a multiple of the divisible height in px
        centered_height_offset_px = round(
            (sensor_height_px / 2 - height_px / 2) / self.step_height_px) * self.step_height_px
        self.pco.sdk.set_roi(centered_width_offset_px, centered_height_offset_px, centered_width_offset_px+width_px, centered_height_offset_px+height_px)
        self.log.info(f"roi set to: {width_px} x {height_px} [width x height]")
        self.log.info(f"roi offset set to: {centered_width_offset_px} x {centered_height_offset_px} [width x height]")

    @property
    def line_interval_us(self):
        line_interval_s = self.pco.sdk.get_cmos_line_timing()
        # returned value is in s, convert to us
        return line_interval_us*1e6

    @line_interval_us.setter
    def line_interval_us(self, line_interval_us: float):

        if line_interval_us < self.max_line_interval_us or \
                line_interval_us > self.max_line_interval_us:
            self.log.error(f"line interval must be >{self.min_line_interval_us} us \
                             and <{self.max_line_interval_us} us")
            raise ValueError(f"exposure time must be >{self.min_line_interval_us} us \
                             and <{self.max_line_interval_us} us")
        # timebase is us if interval > 4 us
        self.pco.sdk.set_cmos_line_timing("on", line_interval_us)
        self.log.info(f"line interval set to: {line_interval_us} us")

    @property
    def trigger(self):
        mode = self.pco.sdk.get_trigger_mode()
        source = None
        polarity = None
        return {"mode": next(key for key, value in TRIGGERS['modes'].items() if value == mode),
                "source": None,
                "polarity": None}

    @trigger.setter
    def trigger(self, trigger: dict):

        mode = trigger['mode']
        source = trigger['source']
        polarity = trigger['polarity']

        valid_mode = list(TRIGGERS['modes'].keys())
        if mode not in valid_mode:
            raise ValueError("mode must be one of %r." % valid_mode)
        valid_source = list(TRIGGERS['sources'].keys())
        if source not in valid_source:
            raise ValueError("source must be one of %r." % valid_source)
        valid_polarity = list(TRIGGERS['polarity'].keys())
        if polarity not in valid_polarity:
            raise ValueError("polarity must be one of %r." % valid_polarity)

        self.pco.sdk.set_triger_mode(TRIGGERS['modes'][mode])
        self.log.info(f"trigger set to, mode: {mode}, source: {source}, polarity: {polarity}")

    @property
    def binning(self):
        # pco binning can be different in x, y. take first value.
        binning = self.pco.sdk.get_binning()[0]
        return next(key for key, value in BINNING.items() if value == binning)

    @binning.setter
    def binning(self, binning: str):
        # pco binning can be different in x, y. set same for both,
        self.pco.sdk.set_binning(BINNING[binning], BINNING[binning])
        self.log.info(f"binning set to: {binning}")

    @property
    def sensor_width_px(self):
        return self.max_width_px

    @property
    def sensor_height_px(self):
        return self.max_height_px

    @property
    def signal_mainboard_temperature_c(self):
        """get the mainboard temperature in degrees C."""
        state = {}
        state['Mainboard Temperature [C]'] = self.pco.sdk.get_temperature()['camera temperature']
        return state

    @property
    def signal_sensor_temperature_c(self):
        """get the sensor temperature in degrees C."""
        state = {}
        state['Sensor Temperature [C]'] = self.pco.sdk.get_temperature()['sensor temperature']
        return state

    @property
    def readout_mode(self):
        # returns dict with only key as 'format'
        readout_mode = self.pco.sdk.set_interface_output_format()['format']
        return next(key for key, value in READOUT_MODES.items() if value == readout_mode)

    @readout_mode.setter
    def readout_mode(self, readout_mode: str):
        # pco api requires edge input for scmos readout control
        valid_mode = list(READOUT_MODES.keys())
        if mode not in valid_mode:
            raise ValueError("mode must be one of %r." % valid_mode)
        self.pco.sdk.set_interface_output_format(interface='edge', format=READOUT_MODES[readout_mode])
        self.log.info(f"readout mode set to: {readout_mode}")

    def prepare(self):
        # pco api prepares buffer and autostarts. api call is in start()
        # pco only 16-bit A/D
        bit_to_byte = 2
        frame_size_mb = self.roi['width_px']*self.roi['height_px']/BINNING[self.binning]**2*bit_to_byte/1e6
        self.buffer_size_frames = round(BUFFER_SIZE_MB / frame_size_mb)
        self.log.info(f"buffer set to: {self.buffer_size_frames} frames")
        pass

    def start(self, frame_count: int, live: bool = False):
        self.dropped_frames = 0
        self.pco.record(number_of_images=self.buffer_size_frames, mode='fifo')

    def stop(self):
        self.pco.stop()

    def close(self):
        self.pco.close()

    def grab_frame(self):
        """Retrieve a frame as a 2D numpy array with shape (rows, cols)."""
        # pco api call is blocking on its own
        timeout_s = 1
        self.pco.wait_for_new_image(delay=True, timeout=timeout_s)
        # always use 0 index for fifo buffer
        image, metadata = self.pco.image(image_index=0)
        return image

    def signal_acquisition_state(self):
        """return a dict with the state of the acquisition buffers"""
        self.pre_time = time.time()
        frame_index = self.pco.recorded_image_count()
        out_buffer_size = None
        in_buffer_size = None
        dropped_frames = self.pco.rec.get_status()["bFIFOOverflow"]
        frame_rate = out_buffer_size/(self.pre_time - self.post_time)
        data_rate = frame_rate*self.roi['width_px']*self.roi['height_px']/BINNING[self.binning]**2/1e6
        state = {}
        state['Frame Index'] = frame_index
        state['Input Buffer Size'] = in_buffer_size
        state['Output Buffer Size'] = out_buffer_size
        # number of underrun, i.e. dropped frames
        state['Dropped Frames'] = self.dropped_frames
        state['Data Rate [MB/s]'] = frame_rate
        state['Frame Rate [fps]'] = data_rate
        self.log.info(f"id: {self.id}, "
                      f"frame: {state['Frame Index']}, "
                      f"input: {state['Input Buffer Size']}, "
                      f"output: {state['Output Buffer Size']}, "
                      f"dropped: {state['Dropped Frames']}, "
                      f"data rate: {state['Data Rate [MB/s]']:.2f} [MB/s], "
                      f"frame rate: {state['Frame Rate [fps]']:.2f} [fps].")
        self.post_time = time.time()
        return state

    def log_metadata(self):
        # log pco configuration settings
        # this is not a comprehensive dump of all metadata
        # todo is to figure out api calls to autodump everything
        self.log.info('pco camera parameters')
        configuration = self.pco.configuration
        for key in configuration:
            self.log.info(f'{key}, {configuration[key]}')