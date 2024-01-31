import logging
import numpy
import time
from .base import BaseCamera
from dcam import *

BUFFER_SIZE_FRAMES = 8

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
    "pixel_type": 4326000  # 0x00420270, R/W, DCAM_PIXELTYPE,   # "IMAGE PIXEL TYPE"
    "sensor_temperature": 2097936  # 0x00200310, R/O, celsius,"SENSOR TEMPERATURE"
}

PIXEL_TYPES = {
    "mono8": DCAM_PIXELTYPE.MONO8,
    "mono16": DCAM_PIXELTYPE.MONO16
}

BINNING = {
    "1x1": 1,
    "2x2": 2,
    "4x4": 4
}

TRIGGERS = {
    "modes": {
        "on": DCAM_PROP.TRIGGER_MODE.NORMAL,
        "off": DCAM_PROP.TRIGGERSOURCE.SOFTWARE,
    },
    "sources": {
        "internal": DCAM_PROP.TRIGGERSOURCE.INTERNAL,
        "external": DCAM_PROP.TRIGGERSOURCE.EXTERNAL,
    },
    "polarity": {
        "rising": DCAM_PROP.TRIGGERPOLARITY.POSITIVE,
        "falling": DCAM_PROP.TRIGGERPOLARITY.NEGATIVE,
    }
}

class Camera(BaseCamera):

    def __init__(self, id):
        """Connect to hardware.
        
        :param camera_cfg: cfg for camera.
        """
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.id = id

        if Dcamapi.init() is not False:
            num_cams = Dcamapi.get_devicecount()
            for cam in range(0, num_cams):
                try:
                    dcam = Dcam(i)
                    if dcam.dev_getstring(DCAM_IDSTR.CAMERAID) == self.id:
                        self.log.info(f"camera found for S/N: {self.id}")
                    self.dcam = dcam
                    break
                except:
                    self.log.error(f"no camera found for S/N: {self.id}")
                    raise ValueError(f"no camera found for S/N: {self.id}")
            del dcam
        else:
            self.log.error('Dcamapi.init() fails with error {}'.format(Dcamapi.lasterr()))

        # gather min max values
        # convert from s to ms
        self.MIN_EXPOSURE_TIME_MS = self.dcam.prop_getattr(PROPERTIES["exposure_time"]).valuemin*1e3
        self.MAX_EXPOSURE_TIME_MS = self.dcam.prop_getattr(PROPERTIES["exposure_time"]).valuemax*1e3
        # convert from s to us
        self.MIN_LINE_INTERVAL_US = self.dcam.prop_getattr(PROPERTIES["line_interval"]).valuemin*1e6
        self.MAX_LINE_INTERVAL_US = self.dcam.prop_getattr(PROPERTIES["line_interval"]).valuemax*1e6
        self.MIN_WIDTH_PX = self.dcam.prop_getattr(PROPERTIES["image_width"]).valuemin
        self.MAX_WIDTH_PX = self.dcam.prop_getattr(PROPERTIES["image_width"]).valuemax
        self.MIN_HEIGHT_PX = self.dcam.prop_getattr(PROPERTIES["image_height"]).valuemin
        self.MAX_HEIGHT_PX = self.dcam.prop_getattr(PROPERTIES["image_height"]).valuemax
        self.DIVISIBLE_WIDTH_PX = self.dcam.prop_getattr(PROPERTIES["subarray_hpos"]).valuestep
        self.DIVISIBLE_HEIGHT_PX = self.dcam.prop_getattr(PROPERTIES["subarray_vpos"]).valuestep

    @property
    def exposure_time_ms(self):
        # convert from ms units to s
        return self.dcam.prop_getvalue(PROPERTIES["exposure_time"])*1000

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float):

        if exposure_time_ms < self.MIN_EXPOSURE_TIME_MS or \
                exposure_time_ms > self.MAX_EXPOSURE_TIME_MS:
            self.log.error(f"exposure time must be >{self.MIN_EXPOSURE_TIME_MS} ms \
                             and <{self.MAX_EXPOSURE_TIME_MS} ms")
            raise ValueError(f"exposure time must be >{self.MIN_EXPOSURE_TIME_MS} ms \
                             and <{self.MAX_EXPOSURE_TIME_MS} ms")

        # Note: ms units to s conversion
        self.dcam.prop_setvalue(PROPERTIES["exposure_time"], exposure_time_ms/1000)
        self.log.info(f"exposure time set to: {exposure_time_ms} ms")

    @property
    def roi(self):
        return {'width_px': self.dcam.prop_getvalue(property_dict["subarray_hsize"], width_px),
                'height_px': self.dcam.prop_getvalue(property_dict["subarray_vsize"], height_px),
                'width_offset_px': self.dcam.prop_getvalue(property_dict["subarray_hpos"]),
                'height_offest_px': self.dcam.prop_getvalue(property_dict["subarray_vpos"])}

    @roi.setter
    def roi(self, roi: dict):

        width_px = roi['width_px']
        height_px = roi['height_px']

        sensor_height_px = self.MAX_HEIGHT_PX
        sensor_width_px = self.MAX_WIDTH_PX

        if height_px < self.MIN_WIDTH_PX or \
                (height_px % self.DIVISIBLE_HEIGHT_PX) != 0 or \
                height_px > self.MAX_HEIGHT_PX:
            self.log.error(f"Height must be >{self.MIN_HEIGHT_PX} px, \
                             <{self.MAX_HEIGHT_PX} px, \
                             and a multiple of {self.DIVISIBLE_HEIGHT_PX} px!")
            raise ValueError(f"Height must be >{self.MIN_HEIGHT_PX} px, \
                             <{self.MAX_HEIGHT_PX} px, \
                             and a multiple of {self.DIVISIBLE_HEIGHT_PX} px!")

        if width_px < self.MIN_WIDTH_PX or \
                (width_px % self.DIVISIBLE_WIDTH_PX) != 0 or \
                width_px > self.MAX_WIDTH_PX:
            self.log.error(f"Width must be >{self.MIN_WIDTH_PX} px, \
                             <{self.MAX_WIDTH_PX}, \
                            and a multiple of {self.DIVISIBLE_WIDTH_PX} px!")
            raise ValueError(f"Width must be >{self.MIN_WIDTH_PX} px, \
                             <{self.MAX_WIDTH_PX}, \
                            and a multiple of {self.DIVISIBLE_WIDTH_PX} px!")

        self.dcam.prop_setvalue(property_dict["subarray_hpos"], 0)
        self.dcam.prop_setvalue(property_dict["subarray_hsize"], width_px)
        # width offset must be a multiple of the divisible width in px
        centered_width_offset_px = round((sensor_width_px / 2 - width_px / 2) / self.DIVISIBLE_WIDTH_PX) * self.DIVISIBLE_WIDTH_PX
        self.dcam.prop_setvalue(property_dict["subarray_hpos"], centered_width_offset_px)
        self.dcam.prop_setvalue(property_dict["subarray_vpos"], 0)
        self.dcam.prop_setvalue(property_dict["subarray_vsize"], height_px)
        # Height offset must be a multiple of the divisible height in px
        centered_height_offset_px = round(
            (sensor_height_px / 2 - height_px / 2) / self.DIVISIBLE_HEIGHT_PX) * self.DIVISIBLE_HEIGHT_PX
        self.dcam.prop_setvalue(property_dict["subarray_vpos"], centered_height_offset_px)
        self.log.info(f"roi set to: {width_px} x {height_px} [width x height]")
        self.log.info(f"roi offset set to: {centered_width_offset_px} x {centered_height_offset_px} [width x height]")

    @property
    def pixel_type(self):
        pixel_type = self.dcam.prop_getvalue(property_dict["pixel_type"])
        # invert the dictionary and find the abstracted key to output
        return next(key for key, value in PIXEL_TYPES.items() if value == pixel_type)

    @pixel_type.setter
    def pixel_type(self, pixel_type_bits: str):

        valid = list(PIXEL_TYPES.keys())
        if pixel_type_bits not in valid:
            raise ValueError("pixel_type_bits must be one of %r." % valid)

        # Note: for the Vieworks VP-151MX camera, the pixel type also controls line interval
        self.dcam.prop_setvalue(property_dict["pixel_type"], PIXEL_TYPES[pixel_type_bits])
        self.log.info(f"pixel type set to: {pixel_type_bits}")

    @property
    def line_interval_us(self):
        line_interval_s = self.dcam.prop_getvalue(property_dict["line_interval"])
        # convert from s to ms
        return line_interval_us*1e6

    @line_interval_us.setter
    def line_interval_us(self, line_interval_us: float):

        if line_interval_us < self.MAX_LINE_INTERVAL_US or \
                line_interval_us > self.MAX_LINE_INTERVAL_US:
            self.log.error(f"line interval must be >{self.MIN_LINE_INTERVAL_US} us \
                             and <{self.MAX_LINE_INTERVAL_US} us")
            raise ValueError(f"exposure time must be >{self.MIN_LINE_INTERVAL_US} us \
                             and <{self.MAX_LINE_INTERVAL_US} us")

        self.dcam.prop_setvalue(property_dict["line_interval"], line_interval_us/1e6)
        self.log.info(f"line interval set to: {line_interval_us} us")

    @property
    def trigger(self):
        source = self.dcam.prop_getvalue(property_dict["trigger_source"])
        if source == DCAM_PROP.TRIGGERSOURCE.SOFTWARE:
            mode = 'off'
        else:
            mode = 'on'
        polarity = self.dcam.prop_getvalue(property_dict["trigger_polarity"])
        return {"mode": next(key for key, value in TRIGGER_MODES.items() if value == mode),
                "source": next(key for key, value in TRIGGER_SOURCES.items() if value == source),
                "polarity": next(key for key, value in TRIGGER_POLARITY.items() if value == polarity)}

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
            self.dcam.prop_setvalue(property_dict["trigger_mode"], TRIGGERS['modes'][mode])
            self.dcam.prop_setvalue(property_dict["trigger_source"], TRIGGERS['sources'][source])
            self.dcam.prop_setvalue(property_dict["trigger_polarity"], TRIGGERS['sources'][polarity])
        if TRIGGERS['modes'][mode] == "off":
            self.dcam.prop_setvalue(property_dict["trigger_source"], TRIGGERS['modes'][mode])
            self.dcam.prop_setvalue(property_dict["trigger_polarity"], TRIGGERS['sources'][polarity])
        self.log.info(f"trigger set to, mode: {mode}, source: {source}, polarity: {polarity}")

    @property
    def binning(self):
        binning = self.dcam.prop_getvalue(property_dict["binning"])
        return next(key for key, value in BINNING.items() if value == binning)

    @binning.setter
    def binning(self, binning: str):
        self.dcam.prop_setvalue(property_dict["binning"], BINNING[binning])
        self.log.info(f"binning set to: {binning}")

    @property
    def sensor_width_px(self):
        return self.MAX_WIDTH_PX

    @property
    def sensor_height_px(self):
        return self.MAX_HEIGHT_PX

    @property
    def sensor_temperature_c(self):
        """get the sensor temperature in degrees C."""
        return self.dcam.prop_getvalue(PROPERTIES["sensor_temperature"])

    def prepare(self):
        # realloc buffers appears to be allocating ram on the pc side, not camera side.
        self.dcam.buff_aloc(BUFFER_SIZE_FRAMES)
        self.log.info(f"buffer set to: {BUFFER_SIZE_FRAMES} frames")

    def start(self, frame_count: int, live: bool = False):
        self.dropped_frames = 0
        self.dcam.cap_start()

    def stop(self):
        self.dcam.cap_stop()

    def close(self):
        self.dcam.dev_close()
        Dcamapi.uninit()

    def grab_frame(self):
        """Retrieve a frame as a 2D numpy array with shape (rows, cols)."""
        # Note: creating the buffer and then "pushing" it at the end has the
        #   effect of moving the internal camera frame buffer from the output
        #   pool back to the input pool, so it can be reused.
        timeout_ms = 1000
        if self.dcam.wait_capevent_frameready(timeout_ms) is not False:
            image = self.dcam.buf_getlastframedata()
        return image

    def get_camera_acquisition_state(self):
        """return a dict with the state of the acquisition buffers"""
        cap_info = DCAMCAP_TRANSFERINFO()
        dcamcap_transferinfo(self.__hdcam, byref(cap_info))
        self.pre_time = time.time()
        frame_index = cap_info.nNewestFrameIndex
        out_buffer_size = cap_info.nFrameCount
        in_buffer_size = BUFFER_SIZE_FRAMES - out_buffer_size
        if out_buffer_size > BUFFER_SIZE_FRAMES:
            new_dropped_frames = out_buffer_size - BUFFER_SIZE_FRAMES
        self.dropped_frames += new_dropped_frames
        frame_rate = out_buffer_size/(self.pre_time - self.post_time)
        data_rate = frame_rate*self.roi['width_px']*self.roi['height_px']/BINNING[self.binning]**2/1e6
        state = {}
        state['frame_index'] = frame_index
        state['in_buffer_size'] = in_buffer_size
        state['out_buffer_size'] = out_buffer_size
        # number of underrun, i.e. dropped frames
        state['dropped_frames'] = self.dropped_frames
        state['data_rate'] = frame_rate
        state['frame_rate'] = data_rate
        self.log.info(f"id: {self.id}, "
                      f"frame: {state['frame_index']}, "
                      f"input: {state['in_buffer_size']}, "
                      f"output: {state['out_buffer_size']}, "
                      f"dropped: {state['dropped_frames']}, "
                      f"data rate: {state['data_rate']:.2f} [MB/s], "
                      f"frame rate: {state['frame_rate']:.2f} [fps].")
        self.post_time = time.time()
        return state

    def log_metadata(self):
        # log dcam camera settings
        self.log.info('dcam camera parameters')
        idprop = self.dcam.prop_getnextid(0)
        while idprop is not False:
            output = '0x{:08X}: '.format(idprop)
            propname = self.dcam.prop_getname(idprop)
            propvalue = self.dcam.prop_getvalue(propname)
            self.log.info(f'{propname}, {propvalue}')
            idprop = dcam.prop_getnextid(idprop)