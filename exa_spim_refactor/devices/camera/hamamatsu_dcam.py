import logging
import numpy
import time
from exa_spim_refactor.devices.camera.singleton import Singleton
from exa_spim_refactor.devices.camera.base import BaseCamera
from exa_spim_refactor.devices.camera.sdks.dcam.dcam import *

BUFFER_SIZE_MB = 2400

# dcam properties dict for convenience in calls
PROPERTIES = {
    "exposure_time": 2031888,  # 0x001F0110, R/W, sec, "EXPOSURE TIME"
    "sensor_mode": 4194832,  # 0x00400210, R/W, mode,  "SENSOR MODE"
    "binning": 4198672,  # 0x00401110, R/W, mode, "BINNING"
    "readout_direction": 4194608,  # 0x00400130, R/W, mode,   "READOUT DIRECTION"
    "trigger_active": 1048864,  # 0x00100120, R/W, mode,   "TRIGGER ACTIVE"
    "trigger_mode": 1049104,  # 0x00100210, R/W, mode,    "TRIGGER MODE"
    "trigger_polarity": 1049120,  # 0x00100220, R/W, mode, "TRIGGER POLARITY"
    "trigger_source": 1048848,  # 0x00100110, R/W, mode,   "TRIGGER SOURCE"
    "line_interval": 4208720,  # 0x00403850, R/W, sec,  # "INTERNAL LINE INTERVAL"
    "image_width": 4325904,  # 0x00420210, R/O, long, "IMAGE WIDTH"
    "image_height": 4325920,  # 0x00420220, R/O, long,    "IMAGE HEIGHT"
    "subarray_hpos": 4202768,  # 0x00402110, R/W, long,    "SUBARRAY HPOS"
    "subarray_hsize": 4202784,  # 0x00402120, R/W, long,   "SUBARRAY HSIZE"
    "subarray_vpos": 4202800,  # 0x00402130, R/W, long,    "SUBARRAY VPOS"
    "subarray_vsize": 4202816,  # 0x00402140, R/W, long,   "SUBARRAY VSIZE"
    "subarray_mode": 4202832,  # 0x00402150, R/W, mode,    "SUBARRAY MODE"
    "pixel_type": 4326000,  # 0x00420270, R/W, DCAM_PIXELTYPE,   # "IMAGE PIXEL TYPE"
    "sensor_temperature": 2097936  # 0x00200310, R/O, celsius,"SENSOR TEMPERATURE"
}

PIXEL_TYPES = {
    "mono8": DCAM_PIXELTYPE.MONO8,
    "mono16": DCAM_PIXELTYPE.MONO16
}

BINNING = {
    1: 1,
    2: 2,
    4: 4
}

# full dcam trigger modes mapping
# NORMAL = 1
# PIV = 3
# START = 6
# full dcam trigger sources mapping
# INTERNAL = 1
# EXTERNAL = 2
# SOFTWARE = 3
# MASTERPULSE = 4
# full dcam trigger polarity mapping
# NEGATIVE = 1
# POSITIVE = 2
# full dcam trigger active mapping
# EDGE = 1
# LEVEL = 2
# SYNCREADOUT = 3
# POINT = 4

TRIGGERS = {
    "modes": {
        "on": DCAMPROP.TRIGGER_MODE.NORMAL,
        "off": DCAMPROP.TRIGGERSOURCE.SOFTWARE,
    },
    "sources": {
        "internal": DCAMPROP.TRIGGERSOURCE.INTERNAL,
        "external": DCAMPROP.TRIGGERSOURCE.EXTERNAL,
    },
    "polarity": {
        "rising": DCAMPROP.TRIGGERPOLARITY.POSITIVE,
        "falling": DCAMPROP.TRIGGERPOLARITY.NEGATIVE,
    }
}

# full dcam readout modes mapping
# AREA = 1
# LINE = 3
# TDI = 4
# TDI_EXTENDED = 10
# PROGRESSIVE = 12
# SPLITVIEW = 14
# DUALLIGHTSHEET = 16
# PHOTONNUMBERRESOLVING = 18
# WHOLELINES = 19
# full dcam readout directions  mapping
# FORWARD = 1
# BACKWARD = 2
# BYTRIGGER = 3
# DIVERGE = 5
# FORWARDBIDIRECTION = 6
# REVERSEBIDIRECTION = 7

READOUT_MODES = {
    "rolling": DCAMPROP.SENSORMODE.AREA,
    "light sheet forward": DCAMPROP.READOUT_DIRECTION.FORWARD,
    "light sheet backward": DCAMPROP.READOUT_DIRECTION.BACKWARD
}

# singleton wrapper around Dcamapi
class DcamapiSingleton(Dcamapi, metaclass=Singleton):
    def __init__(self):
        super(DcamapiSingleton, self).__init__()

class Camera(BaseCamera):

    def __init__(self, id = str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.id = id
        if DcamapiSingleton.init() is not False:
            num_cams = DcamapiSingleton.get_devicecount()
            for cam in range(0, num_cams):
                dcam = Dcam(cam)
                cam_id = dcam.dev_getstring(DCAM_IDSTR.CAMERAID)
                if cam_id.replace("S/N: ","") == self.id:
                    self.log.info(f"camera found for S/N: {self.id}")
                    self.dcam = dcam
                    # open camera
                    self.dcam.dev_open()
                    break
                else:
                    self.log.error(f"no camera found for S/N: {self.id}")
                    raise ValueError(f"no camera found for S/N: {self.id}")
            del dcam
        else:
            self.log.error('DcamapiSingleton.init() fails with error {}'.format(DcamapiSingleton.lasterr()))
        # grab parameter values
        self._get_min_max_step_values()

    @property
    def exposure_time_ms(self):
        # convert from ms units to s
        return self.dcam.prop_getvalue(PROPERTIES["exposure_time"])*1000

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float):

        if exposure_time_ms < self.min_exposure_time_ms or \
                exposure_time_ms > self.max_exposure_time_ms:
            self.log.error(f"exposure time must be >{self.min_exposure_time_ms} ms \
                             and <{self.max_exposure_time_ms} ms")
            raise ValueError(f"exposure time must be >{self.min_exposure_time_ms} ms \
                             and <{self.max_exposure_time_ms} ms")

        # Note: ms units to s conversion
        self.dcam.prop_setvalue(PROPERTIES["exposure_time"], exposure_time_ms/1000)
        self.log.info(f"exposure time set to: {exposure_time_ms} ms")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def roi(self):

        return {'width_px': self.dcam.prop_getvalue(PROPERTIES["subarray_hsize"]),
                'height_px': self.dcam.prop_getvalue(PROPERTIES["subarray_vsize"]),
                'width_offset_px': self.dcam.prop_getvalue(PROPERTIES["subarray_hpos"]),
                'height_offest_px': self.dcam.prop_getvalue(PROPERTIES["subarray_vpos"])}

    @roi.setter
    def roi(self, roi: dict):

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

        self.dcam.prop_setvalue(PROPERTIES["subarray_hpos"], 0)
        self.dcam.prop_setvalue(PROPERTIES["subarray_hsize"], width_px)
        # width offset must be a multiple of the divisible width in px
        centered_width_offset_px = round((sensor_width_px / 2 - width_px / 2) / self.step_width_px) * self.step_width_px
        self.dcam.prop_setvalue(PROPERTIES["subarray_hpos"], centered_width_offset_px)
        self.dcam.prop_setvalue(PROPERTIES["subarray_vpos"], 0)
        self.dcam.prop_setvalue(PROPERTIES["subarray_vsize"], height_px)
        # Height offset must be a multiple of the divisible height in px
        centered_height_offset_px = round(
            (sensor_height_px / 2 - height_px / 2) / self.step_height_px) * self.step_height_px
        self.dcam.prop_setvalue(PROPERTIES["subarray_vpos"], centered_height_offset_px)
        self.log.info(f"roi set to: {width_px} x {height_px} [width x height]")
        self.log.info(f"roi offset set to: {centered_width_offset_px} x {centered_height_offset_px} [width x height]")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def pixel_type(self):
        pixel_type = self.dcam.prop_getvalue(PROPERTIES["pixel_type"])
        # invert the dictionary and find the abstracted key to output
        return next(key for key, value in PIXEL_TYPES.items() if value == pixel_type)

    @pixel_type.setter
    def pixel_type(self, pixel_type_bits: str):

        valid = list(PIXEL_TYPES.keys())
        if pixel_type_bits not in valid:
            raise ValueError("pixel_type_bits must be one of %r." % valid)

        self.dcam.prop_setvalue(PROPERTIES["pixel_type"], PIXEL_TYPES[pixel_type_bits])
        self.log.info(f"pixel type set to: {pixel_type_bits}")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def line_interval_us(self):
        line_interval_s = self.dcam.prop_getvalue(PROPERTIES["line_interval"])
        # convert from s to ms
        return line_interval_s*1e6

    @line_interval_us.setter
    def line_interval_us(self, line_interval_us: float):

        if line_interval_us < self.min_line_interval_us or \
                line_interval_us > self.max_line_interval_us:
            self.log.error(f"line interval must be >{self.min_line_interval_us} us \
                             and <{self.max_line_interval_us} us")
            raise ValueError(f"exposure time must be >{self.min_line_interval_us} us \
                             and <{self.max_line_interval_us} us")

        # convert from us to s
        self.dcam.prop_setvalue(PROPERTIES["line_interval"], line_interval_us/1e6)
        self.log.info(f"line interval set to: {line_interval_us} us")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def trigger(self):
        source = self.dcam.prop_getvalue(PROPERTIES["trigger_source"])
        if source == 3:
            mode = 'off'
        else:
            mode = 'on'
        polarity = self.dcam.prop_getvalue(PROPERTIES["trigger_polarity"])
        return {"mode": mode,
                "source": next(key for key, value in TRIGGERS['sources'].items() if value == source),
                "polarity": next(key for key, value in TRIGGERS['polarity'].items() if value == polarity)}

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

        # TODO figure out TRIGGERACTIVE bools
        if TRIGGERS['modes'][mode] == "on":
            self.dcam.prop_setvalue(PROPERTIES["trigger_mode"], TRIGGERS['modes'][mode])
            self.dcam.prop_setvalue(PROPERTIES["trigger_source"], TRIGGERS['sources'][source])
            self.dcam.prop_setvalue(PROPERTIES["trigger_polarity"], TRIGGERS['sources'][polarity])
        if TRIGGERS['modes'][mode] == "off":
            self.dcam.prop_setvalue(PROPERTIES["trigger_source"], TRIGGERS['modes'][mode])
            self.dcam.prop_setvalue(PROPERTIES["trigger_polarity"], TRIGGERS['sources'][polarity])
        self.log.info(f"trigger set to, mode: {mode}, source: {source}, polarity: {polarity}")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def binning(self):
        binning = self.dcam.prop_getvalue(PROPERTIES["binning"])
        return next(key for key, value in BINNING.items() if value == binning)

    @binning.setter
    def binning(self, binning: str):
        valid_binning = list(BINNING.keys())
        if binning not in valid_binning:
            raise ValueError("binning must be one of %r." % valid_binning)
        self.dcam.prop_setvalue(PROPERTIES["binning"], BINNING[binning])
        self.log.info(f"binning set to: {binning}")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def sensor_width_px(self):
        return self.max_width_px

    @property
    def sensor_height_px(self):
        return self.min_width_px

    @property
    def signal_sensor_temperature_c(self):
        """get the sensor temperature in degrees C."""
        state = {}
        state['Sensor Temperature [C]'] = self.dcam.prop_getvalue(PROPERTIES["sensor_temperature"])
        return state

    @property
    def readout_mode(self):
        sensor_mode = self.dcam.prop_getvalue(PROPERTIES['sensor_mode'])
        readout_direction = self.dcam.prop_getvalue(PROPERTIES['readout_direction'])
        if sensor_mode == DCAMPROP.SENSORMODE.AREA:
            readout_mode = "rolling"
        if sensor_mode == DCAMPROP.SENSORMODE.PROGRESSIVE:
            if readout_direction == DCAMPROP.READOUT_DIRECTION.FORWARD:
                readout_mode = "light sheet forward"
            if readout_direction == DCAMPROP.READOUT_DIRECTION.BACKWARD:
                readout_mode = "light sheet backward"
        return readout_mode

    @readout_mode.setter
    def readout_mode(self, readout_mode: str):
        valid_mode = list(READOUT_MODES.keys())
        if readout_mode not in valid_mode:
            raise ValueError("readout_mode must be one of %r." % valid_mode)
        if readout_mode == "rolling":
            self.dcam.prop_setvalue(PROPERTIES['sensor_mode'], READOUT_MODES[readout_mode])
        else:
            # set sensor mode to light-sheet -> 12
            self.dcam.prop_setvalue(PROPERTIES['sensor_mode'], DCAMPROP.SENSORMODE.PROGRESSIVE)
            # set readout direction to forward or backward
            self.dcam.prop_setvalue(PROPERTIES['readout_direction'], READOUT_MODES[readout_mode])
        # refresh parameter values
        self._get_min_max_step_values()

    def prepare(self):
        # determine bits to bytes
        if self.pixel_type == 'mono8':
            bit_to_byte = 1
        else:
            bit_to_byte = 2
        frame_size_mb = self.roi['width_px']*self.roi['height_px']/BINNING[self.binning]**2*bit_to_byte/1e6
        self.buffer_size_frames = round(BUFFER_SIZE_MB / frame_size_mb)
        # realloc buffers appears to be allocating ram on the pc side, not camera side.
        self.dcam.buf_alloc(self.buffer_size_frames)
        self.log.info(f"buffer set to: {self.buffer_size_frames} frames")

    def start(self):
        # initialize variables for acquisition run
        self.dropped_frames = 0
        self.pre_frame_time = 0
        self.pre_frame_count = 0
        self.dcam.cap_start()

    def stop(self):
        self.dcam.buf_release()
        self.dcam.cap_stop()

    def close(self):
        self.dcam.dev_close()
        DcamapiSingleton.uninit()

    def grab_frame(self):
        """Retrieve a frame as a 2D numpy array with shape (rows, cols)."""
        # Note: creating the buffer and then "pushing" it at the end has the
        #   effect of moving the internal camera frame buffer from the output
        #   pool back to the input pool, so it can be reused.
        timeout_ms = 1000
        if self.dcam.wait_capevent_frameready(timeout_ms) is not False:
            image = self.dcam.buf_getlastframedata()
        return image

    def signal_acquisition_state(self):
        """return a dict with the state of the acquisition buffers"""
        cap_info = DCAMCAP_TRANSFERINFO()
        # __hdcam inside class Dcam referenced as _Dcam__hdcam
        dcamcap_transferinfo(self.dcam._Dcam__hdcam, byref(cap_info))
        self.post_frame_time = time.time()
        frame_index = cap_info.nFrameCount
        out_buffer_size = frame_index - self.pre_frame_count
        in_buffer_size = self.buffer_size_frames - out_buffer_size
        if out_buffer_size > self.buffer_size_frames:
            new_dropped_frames = out_buffer_size - self.buffer_size_frames
            self.dropped_frames += new_dropped_frames
        frame_rate = out_buffer_size/(self.post_frame_time - self.pre_frame_time)
        # determine bits to bytes
        if self.pixel_type == 'mono8':
            bit_to_byte = 1
        else:
            bit_to_byte = 2
        data_rate = frame_rate*self.roi['width_px']*self.roi['height_px']/BINNING[self.binning]**2*bit_to_byte/1e6
        state = {}
        state['Frame Index'] = frame_index
        state['Input Buffer Size'] = in_buffer_size
        state['Output Buffer Size'] = out_buffer_size
        # number of underrun, i.e. dropped frames
        state['Dropped Frames'] = self.dropped_frames
        state['Data Rate [MB/s]'] = data_rate
        state['Frame Rate [fps]'] = frame_rate
        self.log.info(f"id: {self.id}, "
                      f"frame: {state['Frame Index']}, "
                      f"input: {state['Input Buffer Size']}, "
                      f"output: {state['Output Buffer Size']}, "
                      f"dropped: {state['Dropped Frames']}, "
                      f"data rate: {state['Data Rate [MB/s]']:.2f} [MB/s], "
                      f"frame rate: {state['Frame Rate [fps]']:.2f} [fps].")
        self.pre_frame_time = time.time()
        self.pre_frame_count = cap_info.nFrameCount

        return state

    def log_metadata(self):
        # log dcam camera settings
        self.log.info('dcam camera parameters')
        idprop = self.dcam.prop_getnextid(0)
        while idprop is not False:
            propname = self.dcam.prop_getname(idprop)
            propvalue = self.dcam.prop_getvalue(idprop)
            self.log.info(f'{propname}, {propvalue}')
            idprop = self.dcam.prop_getnextid(idprop)

    def _get_min_max_step_values(self):
        # gather min max values
        # convert from s to ms
        self.min_exposure_time_ms = self.dcam.prop_getattr(PROPERTIES["exposure_time"]).valuemin*1e3
        self.max_exposure_time_ms = self.dcam.prop_getattr(PROPERTIES["exposure_time"]).valuemax*1e3
        # convert from s to us
        self.min_line_interval_us = self.dcam.prop_getattr(PROPERTIES["line_interval"]).valuemin*1e6
        self.max_line_interval_us = self.dcam.prop_getattr(PROPERTIES["line_interval"]).valuemax*1e6
        self.min_width_px = self.dcam.prop_getattr(PROPERTIES["image_width"]).valuemin
        self.max_width_px = self.dcam.prop_getattr(PROPERTIES["image_width"]).valuemax
        self.min_height_px = self.dcam.prop_getattr(PROPERTIES["image_height"]).valuemin
        self.max_height_px = self.dcam.prop_getattr(PROPERTIES["image_height"]).valuemax
        self.min_offset_x_px = self.dcam.prop_getattr(PROPERTIES["subarray_hpos"]).valuemin
        self.max_offset_x_px = self.dcam.prop_getattr(PROPERTIES["subarray_hpos"]).valuemax
        self.min_offset_y_px = self.dcam.prop_getattr(PROPERTIES["subarray_vpos"]).valuemin
        self.max_offset_y_px = self.dcam.prop_getattr(PROPERTIES["subarray_vpos"]).valuemax
        # convert from s to us
        self.step_exposure_time_ms = self.dcam.prop_getattr(PROPERTIES["exposure_time"]).valuestep*1e3
        self.step_line_interval_us = self.dcam.prop_getattr(PROPERTIES["line_interval"]).valuestep*1e6
        self.step_width_px = self.dcam.prop_getattr(PROPERTIES["image_width"]).valuestep
        self.step_height_px = self.dcam.prop_getattr(PROPERTIES["image_height"]).valuestep
        self.step_offset_x_px = self.dcam.prop_getattr(PROPERTIES["subarray_hpos"]).valuestep
        self.step_offset_y_px = self.dcam.prop_getattr(PROPERTIES["subarray_vpos"]).valuestep

        self.log.info(f"min exposure time is: {self.min_exposure_time_ms} ms")
        self.log.info(f"max exposure time is: {self.max_exposure_time_ms} ms")
        self.log.info(f"min line interval is: {self.min_line_interval_us} us")
        self.log.info(f"max line interval is: {self.max_line_interval_us} us")
        self.log.info(f"min width is: {self.min_width_px} px")
        self.log.info(f"max width is: {self.max_width_px} px")
        self.log.info(f"min height is: {self.min_height_px} px")
        self.log.info(f"max height is: {self.max_height_px} px")
        self.log.info(f"min offset x is: {self.min_offset_x_px} px")
        self.log.info(f"max offset x is: {self.max_offset_x_px} px")
        self.log.info(f"min offset y is: {self.min_offset_y_px} px")
        self.log.info(f"max offset y is: {self.max_offset_y_px} px")
        self.log.info(f"step exposure time is: {self.step_exposure_time_ms} ms")
        self.log.info(f"step line interval is: {self.step_line_interval_us} us")
        self.log.info(f"step width is: {self.step_width_px} px")
        self.log.info(f"step height is: {self.step_height_px} px")
        self.log.info(f"step offset x is: {self.step_offset_x_px} px")
        self.log.info(f"step offset y is: {self.step_offset_y_px} px")