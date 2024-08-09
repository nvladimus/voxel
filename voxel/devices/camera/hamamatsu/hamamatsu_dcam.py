import logging
import time
from voxel.descriptors.deliminated_property import DeliminatedProperty
from voxel.devices.camera.base import BaseCamera
from voxel.devices.camera.hamamatsu.dcam.dcam import (
    DCAM_IDSTR,
    DCAMCAP_TRANSFERINFO,
    DCAMERR,
    Dcam,
    Dcamapi,
    byref,
    dcamcap_transferinfo,
)
from voxel.devices.utils.singleton import Singleton

BUFFER_SIZE_MB = 2400

# subarray parameter values
SUBARRAY_OFF = 1
SUBARRAY_ON = 2

# dcam properties dict for convenience in calls
PROPERTIES = {
    "exposure_time": 2031888,  # 0x001F0110, R/W, sec, "EXPOSURE TIME"
    "sensor_mode": 4194832,  # 0x00400210, R/W, mode,  "SENSOR MODE"
    "binning": 4198672,  # 0x00401110, R/W, mode, "BINNING"
    "readout_direction": 4194608,  # 0x00400130, R/W, mode, "READOUT DIRECTION"
    "trigger_active": 1048864,  # 0x00100120, R/W, mode, "TRIGGER ACTIVE"
    "trigger_mode": 1049104,  # 0x00100210, R/W, mode, "TRIGGER MODE"
    "trigger_polarity": 1049120,  # 0x00100220, R/W, mode, "TRIGGER POLARITY"
    "trigger_source": 1048848,  # 0x00100110, R/W, mode, "TRIGGER SOURCE"
    "line_interval": 4208720,  # 0x00403850, R/W, sec, "INTERNAL LINE INTERVAL"
    "image_width": 4325904,  # 0x00420210, R/O, long, "IMAGE WIDTH"
    "image_height": 4325920,  # 0x00420220, R/O, long, "IMAGE HEIGHT"
    "subarray_hpos": 4202768,  # 0x00402110, R/W, long, "SUBARRAY HPOS"
    "subarray_hsize": 4202784,  # 0x00402120, R/W, long, "SUBARRAY HSIZE"
    "subarray_vpos": 4202800,  # 0x00402130, R/W, long, "SUBARRAY VPOS"
    "subarray_vsize": 4202816,  # 0x00402140, R/W, long, "SUBARRAY VSIZE"
    "subarray_mode": 4202832,  # 0x00402150, R/W, mode, "SUBARRAY MODE"
    "pixel_type": 4326000,  # 0x00420270, R/W, DCAM_PIXELTYPE, "PIXEL TYPE"
    "sensor_temperature": 2097936,  # 0x00200310, R/O, celsius, "TEMPERATURE"
}

# generate valid pixel types by querying dcam
# should be of the form
# {"mono8": DCAM_PIXELTYPE.MONO8,
#  "mono12": DCAM_PIXELTYPE.MONO12,
#  "mono16": DCAM_PIXELTYPE.MONO16 ...
# }
PIXEL_TYPES = dict()

# generate valid binning by querying dcam
# should be of the form
# {"1x1": 1,
#  "2x2": 2,
#  "4x4": 4 ...
# }
BINNING = dict()

# generate valid triggers by querying dcam
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
TRIGGERS = {"mode": dict(), "source": dict(), "polarity": dict()}

# generate valid sensor modes by querying dcam
# full dcam sensor modes mapping
# AREA = 1
# LINE = 3
# TDI = 4
# TDI_EXTENDED = 10
# PROGRESSIVE = 12
# SPLITVIEW = 14
# DUALLIGHTSHEET = 16
# PHOTONNUMBERRESOLVING = 18
# WHOLELINES = 19
SENSOR_MODES = dict()

# generate valid readout directions by querying dcam
# full dcam readout directions  mapping
# FORWARD = 1
# BACKWARD = 2
# BYTRIGGER = 3
# DIVERGE = 5
# FORWARDBIDIRECTION = 6
# REVERSEBIDIRECTION = 7
READOUT_DIRECTIONS = dict()


# singleton wrapper around Dcamapi
class DcamapiSingleton(Dcamapi, metaclass=Singleton):
    def __init__(self):
        """Singleton wrapper around the DCAM SDK. Ensures the same DCAM \n
        instance is returned anytime DCAM is initialized.
        """

        super(DcamapiSingleton, self).__init__()


class Camera(BaseCamera):
    def __init__(self, id: str):
        """Voxel driver for Hamamatsu cameras.

        :param id: Serial number of the camera.
        :type id: str
        :raises ValueError: No camera found.
        """

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # convert to string incase serial # is entered as int
        self.id = str(id)
        if DcamapiSingleton.init() is not False:
            num_cams = DcamapiSingleton.get_devicecount()
            for cam in range(0, num_cams):
                dcam = Dcam(cam)
                cam_id = dcam.dev_getstring(DCAM_IDSTR.CAMERAID)
                if cam_id.replace("S/N: ", "") == self.id:
                    self.log.info(f"camera found for S/N: {self.id}")
                    self.dcam = dcam
                    self.cam_num = cam
                    # open camera
                    self.dcam.dev_open()
                    break
                else:
                    self.log.error(f"no camera found for S/N: {self.id}")
                    raise ValueError(f"no camera found for S/N: {self.id}")
            del dcam
        else:
            self.log.error(
                "DcamapiSingleton.init() fails with error {}".format(
                    DCAMERR(DcamapiSingleton.lasterr()).name
                )
            )
        # initialize parameter values
        self._update_parameters()

    @DeliminatedProperty(
        minimum=lambda self: self.min_exposure_time_ms,
        maximum=lambda self: self.max_exposure_time_ms,
        step=lambda self: self.step_exposure_time_ms,
        unit="ms",
    )
    def exposure_time_ms(self):
        """
        Get the exposure time of the camera in ms

        :return: The exposure time in ms.
        :rtype: float
        """
        # us to ms conversion
        return self.dcam.prop_getvalue(PROPERTIES["exposure_time"]) * 1000

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float):
        """
        Set the exposure time of the camera in ms.

        :param exposure_time_ms: The exposure time in ms
        :type exposure_time_ms: float
        """

        self.dcam.prop_setvalue(PROPERTIES["exposure_time"], exposure_time_ms / 1000)
        self.log.info(f"exposure time set to: {exposure_time_ms} ms")
        # refresh parameter values
        self._update_parameters()

    @DeliminatedProperty(
        minimum=lambda self: self.min_width_px,
        maximum=lambda self: self.max_width_px,
        step=lambda self: self.step_width_px,
        unit="px",
    )
    def roi_width_px(self):
        """
        Get the width of the camera region of interest in pixels.

        :return: The width of the region of interest in pixels
        :rtype: int
        """

        return int(self.dcam.prop_getvalue(PROPERTIES["subarray_hsize"]))

    @roi_width_px.setter
    def roi_width_px(self, value: int):
        """
        Set the width of the camera region of interest in pixels.

        :param value: The width of the region of interest in pixels
        :type value: int
        """
        # reset offset to (0,0)
        self.dcam.prop_setvalue(PROPERTIES["subarray_hpos"], 0)
        self.dcam.prop_setvalue(PROPERTIES["subarray_hsize"], value)
        centered_offset_px = (
            round((self.max_width_px / 2 - value / 2) / self.step_width_px)
            * self.step_width_px
        )
        self.dcam.prop_setvalue(PROPERTIES["subarray_hpos"], centered_offset_px)
        self.log.info(f"width set to: {value} px")
        # refresh parameter values
        self._update_parameters()

    @property
    def roi_width_offset_px(self):
        """
        Get the width offset of the camera region of interest in pixels.

        :return: The width offset of the region of interest in pixels
        :rtype: int
        """

        return int(self.dcam.prop_getvalue(PROPERTIES["subarray_hpos"]))

    @DeliminatedProperty(
        minimum=lambda self: self.min_height_px,
        maximum=lambda self: self.max_height_px,
        step=lambda self: self.step_height_px,
        unit="px",
    )
    @DeliminatedProperty(minimum=float("-inf"), maximum=float("inf"))
    def roi_height_px(self):
        """
        Get the height of the camera region of interest in pixels.

        :return: The height of the region of interest in pixels
        :rtype: int
        """

        return int(self.dcam.prop_getvalue(PROPERTIES["subarray_vsize"]))

    @roi_height_px.setter
    def roi_height_px(self, value: int):
        """
        Set the height of the camera region of interest in pixels.

        :param value: The height of the region of interest in pixels
        :type value: int
        """
        # reset offset to (0,0)
        self.dcam.prop_setvalue(PROPERTIES["subarray_vpos"], 0)
        self.dcam.prop_setvalue(PROPERTIES["subarray_vsize"], value)
        centered_offset_px = (
            round((self.max_height_px / 2 - value / 2) / self.step_height_px)
            * self.step_height_px
        )
        self.dcam.prop_setvalue(PROPERTIES["subarray_vpos"], centered_offset_px)
        self.log.info(f"height set to: {value} px")
        # refresh parameter values
        self._update_parameters()

    @property
    def roi_height_offset_px(self):
        """
        Get the height offset of the camera region of interest in pixels.

        :return: The height offset of the region of interest in pixels.
        :rtype: int
        """

        return int(self.dcam.prop_getvalue(PROPERTIES["subarray_vpos"]))

    @property
    def pixel_type(self):
        """
        Get the pixel type of the camera.

        :return: The pixel type of the camera
        :rtype: str
        """

        pixel_type = self.dcam.prop_getvalue(PROPERTIES["pixel_type"])
        # invert the dictionary and find the abstracted key to output
        return next(key for key, value in PIXEL_TYPES.items() if value == pixel_type)

    @pixel_type.setter
    def pixel_type(self, pixel_type_bits: str):
        """
        The pixel type of the camera.

        :param pixel_type_bits: The pixel type
        * **mono8**
        * **mono12**
        * **mono16**
        :type pixel_type_bits: str
        :raises ValueError: Invalid pixel type
        """

        valid = list(PIXEL_TYPES.keys())
        if pixel_type_bits not in valid:
            raise ValueError("pixel_type_bits must be one of %r." % valid)
        self.dcam.prop_setvalue(PROPERTIES["pixel_type"], PIXEL_TYPES[pixel_type_bits])
        self.log.info(f"pixel type set to: {pixel_type_bits}")
        # refresh parameter values
        self._update_parameters()

    @DeliminatedProperty(
        minimum=lambda self: self.min_line_interval_us,
        maximum=lambda self: self.max_line_interval_us,
        step=lambda self: self.step_line_interval_us,
        unit="us",
    )
    def line_interval_us(self):
        """
        Get the line interval of the camera in us. \n
        This is the time interval between adjacnet \n
        rows activating on the camera sensor.

        :return: The line interval of the camera in us
        :rtype: float
        """

        line_interval_s = self.dcam.prop_getvalue(PROPERTIES["line_interval"])
        # convert from s to ms
        return line_interval_s * 1e6

    @line_interval_us.setter
    def line_interval_us(self, line_interval_us: float):
        """
        Set the line interval of the camera in us. \n
        This is the time interval between adjacnet \n
        rows activating on the camera sensor.

        :param line_interval_us: The linterval of the camera in us
        :type line_interval_us: float
        """
        # convert from us to s
        self.dcam.prop_setvalue(PROPERTIES["line_interval"], line_interval_us / 1e6)
        self.log.info(f"line interval set to: {line_interval_us} us")
        # refresh parameter values
        self._update_parameters()

    @property
    def frame_time_ms(self):
        """
        Get the frame time of the camera in ms. \n
        This is the total time to acquire a single image. \n
        Rolling shutter spans half of the chip, whereas \n
        light sheet spans the full chip.

        :return: The frame time of the camera in ms
        :rtype: float
        """

        if "light sheet" in self.readout_mode:
            return (
                self.line_interval_us * self.roi_height_px
            ) / 1000 + self.exposure_time_ms
        else:
            return (
                    self.line_interval_us * self.roi_height_px / 2
            ) / 1000 + self.exposure_time_ms

    @property
    def trigger(self):
        """
        Get the trigger mode of the camera.

        :return: The trigger mode of the camera.
        :rtype: dict
        """

        source = self.dcam.prop_getvalue(PROPERTIES["trigger_source"])
        mode = self.dcam.prop_getvalue(PROPERTIES["trigger_mode"])
        polarity = self.dcam.prop_getvalue(PROPERTIES["trigger_polarity"])
        return {
            "mode": {v: k for k, v in TRIGGERS["mode"].items()}[mode],
            "source": {v: k for k, v in TRIGGERS["source"].items()}[source],
            "polarity": {v: k for k, v in TRIGGERS["polarity"].items()}[polarity]
        }

    @trigger.setter
    def trigger(self, trigger: dict):
        """
        Set the trigger mode of the camera.

        :param trigger: The trigger mode of the camera
        **Trigger modes**
        * **normal**
        * **start**
        * **piv**
        **Trigger sources**
        * **internal**
        * **external**
        * **software**
        * **masterpulse**
        **Trigger polarities**
        * **negative**
        * **positive**
        :type trigger: dict
        :raises ValueError: Invalid trigger mode
        :raises ValueError: Invalid trigger source
        :raises ValueError: Invalid trigger polarity
        """

        mode = trigger["mode"]
        source = trigger["source"]
        polarity = trigger["polarity"]
        valid_mode = list(TRIGGERS["mode"].keys())
        if mode not in valid_mode:
            raise ValueError("mode must be one of %r." % valid_mode)
        valid_source = list(TRIGGERS["source"].keys())
        if source not in valid_source:
            raise ValueError("source must be one of %r." % valid_source)
        valid_polarity = list(TRIGGERS["polarity"].keys())
        if polarity not in valid_polarity:
            raise ValueError("polarity must be one of %r." % valid_polarity)
        # TODO figure out TRIGGERACTIVE bool
        self.dcam.prop_setvalue(PROPERTIES["trigger_mode"], TRIGGERS["mode"][mode])
        self.dcam.prop_setvalue(
            PROPERTIES["trigger_source"], TRIGGERS["source"][source]
        )
        self.dcam.prop_setvalue(
            PROPERTIES["trigger_polarity"], TRIGGERS["polarity"][polarity]
        )
        self.log.info(
            f"trigger set to, mode: {mode}, source: {source}, \
                polarity: {polarity}"
        )
        # refresh parameter values
        self._update_parameters()

    @property
    def binning(self):
        """
        Get the binning mode of the camera.

        :return: The binning mode of the camera
        :rtype: int
        """

        binning = self.dcam.prop_getvalue(PROPERTIES["binning"])
        return binning

    @binning.setter
    def binning(self, binning: str):
        """
        Set the binning of the camera.

        :param binning: The binning mode of the camera
        * **1x1**
        * **2x2**
        * **4x4**
        :type binning: str
        :raises ValueError: Invalid binning setting
        """

        if binning not in BINNING:
            raise ValueError("binning must be one of %r." % BINNING)
        else:
            self.dcam.prop_setvalue(PROPERTIES["binning"], binning)
            self.log.info(f"binning set to: {binning}")
            # refresh parameter values
            self._update_parameters()

    @property
    def sensor_width_px(self):
        """
        Get the width of the camera sensor in pixels.

        :return: The width of the camera sensor in pixels.
        :rtype: int
        """

        return self.max_width_px

    @property
    def sensor_height_px(self):
        """
        Get the height of the camera sensor in pixels.

        :return: The height of the camera sensor in pixels.
        :rtype: int
        """

        return self.min_width_px

    @property
    def signal_sensor_temperature_c(self):
        """
        Get the sensor temperature of the camera in deg C.

        :return: The sensor temperature of the camera in deg C
        :rtype: float
        """

        state = {}
        state["Sensor Temperature [C]"] = self.dcam.prop_getvalue(
            PROPERTIES["sensor_temperature"]
        )
        return state

    @property
    def sensor_mode(self):
        """
        Get the sensor mode of the camera.

        :return: The sensor mode of the camera
        :rtype: str
        """

        sensor_mode = self.dcam.prop_getvalue(PROPERTIES["sensor_mode"])
        return next(key for key, value in SENSOR_MODES.items() if value == sensor_mode)

    @sensor_mode.setter
    def sensor_mode(self, sensor_mode: str):
        """
        Set the sensor mode of the camera.

        :param sensor_mode: The sensor mode of the camera
        * **area**
        * **line**
        * **tdi**
        * **tdi_extended**
        * **progresive**
        * **splitview**
        * **duallightsheet**
        * **photonnumberresolving**
        * **wholelines**
        :type sensor_mode: str
        :raises ValueError: Invalid sensor mode
        """

        valid_mode = list(SENSOR_MODES.keys())
        if sensor_mode not in valid_mode:
            raise ValueError("sensor_mode must be one of %r." % valid_mode)
        else:
            self.dcam.prop_setvalue(
                PROPERTIES["sensor_mode"], SENSOR_MODES[sensor_mode]
            )
        self.log.info(f"sensor mode set to: {sensor_mode}")
        # refresh parameter values
        self._update_parameters()

    @property
    def readout_direction(self):
        """
        Get the readout direction of the camera.

        :return: The readout direction of the camera
        :rtype: str
        """

        readout_direction = self.dcam.prop_getvalue(PROPERTIES["readout_direction"])
        return next(
            key
            for key, value in READOUT_DIRECTIONS.items()
            if value == readout_direction
        )

    @readout_direction.setter
    def readout_direction(self, readout_direction: str):
        """
        Set the readout direction of the camera.

        :param readout_direction: The readout direction of the camera
        * **forward**
        * **backward**
        * **bytrigger**
        * **diverge**
        * **forwardbidirection**
        * **reversebidirection**
        :type readout_direction: str
        :raises ValueError: Invalid readout direction
        """

        valid_direction = list(READOUT_DIRECTIONS.keys())
        if readout_direction not in valid_direction:
            raise ValueError("readout_direction must be one of %r." % valid_direction)
        else:
            self.dcam.prop_setvalue(
                PROPERTIES["readout_direction"], READOUT_DIRECTIONS[readout_direction]
            )
        self.log.info(f"readout direction set to: {readout_direction}")
        # refresh parameter values
        self._update_parameters()

    def prepare(self):
        """
        Prepare the camera to acquire images. \n
        Initializes the camera buffer.
        """
        # determine bits to bytes
        if self.pixel_type == "mono8":
            bit_to_byte = 1
        else:
            bit_to_byte = 2
        frame_size_mb = (
                self.roi_width_px * self.roi_height_px / self.binning ** 2 * bit_to_byte / 1e6
        )
        self.buffer_size_frames = round(BUFFER_SIZE_MB / frame_size_mb)
        self.dcam.buf_alloc(self.buffer_size_frames)
        self.log.info(f"buffer set to: {self.buffer_size_frames} frames")

    def start(self):
        """
        Start the camera.
        """
        # initialize variables for acquisition run
        self.dropped_frames = 0
        self.pre_frame_time = 0
        self.pre_frame_count_px = 0
        self.dcam.cap_start()

    def abort(self):
        """
        Abort the camera.
        """

        self.stop()

    def stop(self):
        """
        Stop the camera.
        """

        self.dcam.buf_release()
        self.dcam.cap_stop()

    def close(self):
        """
        Close the camera.
        """

        if self.dcam.is_opened():
            self.dcam.dev_close()
            DcamapiSingleton.uninit()

    def reset(self):
        """
        Reset the camera.
        """

        if self.dcam.is_opened():
            self.dcam.dev_close()
            DcamapiSingleton.uninit()
            del self.dcam
            if DcamapiSingleton.init() is not False:
                self.dcam = Dcam(self.cam_num)
                self.dcam.dev_open()

    def grab_frame(self):
        """
        Grab a frame from the camera buffer.

        :return: The camera frame of size (height, width).
        :rtype: numpy.array
        """
        # Note: creating the buffer and then "pushing" it at the end has the
        #   effect of moving the internal camera frame buffer from the output
        #   pool back to the input pool, so it can be reused.
        timeout_ms = 1000
        if self.dcam.wait_capevent_frameready(timeout_ms) is not False:
            image = self.dcam.buf_getlastframedata()
            return image

    def signal_acquisition_state(self):
        """
        Return a dictionary of the acquisition state: \n
        - Frame Index - frame number of the acquisition \n
        - Input Buffer Size - number of free frames in buffer \n
        - Output Buffer Size - number of frames to grab from buffer \n
        - Dropped Frames - number of dropped frames
        - Data Rate [MB/s] - data rate of acquisition
        - Frame Rate [fps] - frames per second of acquisition

        :return: The acquisition state
        :rtype: dict
        """

        cap_info = DCAMCAP_TRANSFERINFO()
        # __hdcam inside class Dcam referenced as _Dcam__hdcam
        dcamcap_transferinfo(self.dcam._Dcam__hdcam, byref(cap_info))
        self.post_frame_time = time.time()
        frame_index = cap_info.nFrameCount
        out_buffer_size = frame_index - self.pre_frame_count_px
        in_buffer_size = self.buffer_size_frames - out_buffer_size
        if out_buffer_size > self.buffer_size_frames:
            new_dropped_frames = out_buffer_size - self.buffer_size_frames
            self.dropped_frames += new_dropped_frames
        frame_rate = out_buffer_size / (self.post_frame_time - self.pre_frame_time)
        # determine bits to bytes
        if self.pixel_type == "mono8":
            bit_to_byte = 1
        else:
            bit_to_byte = 2
        data_rate = (
            frame_rate
            * self.roi_width_px
            * self.roi_height_px
            / self.binning**2
            * bit_to_byte
            / 1e6
        )
        state = {}
        state["Frame Index"] = frame_index
        state["Input Buffer Size"] = in_buffer_size
        state["Output Buffer Size"] = out_buffer_size
        # number of underrun, i.e. dropped frames
        state["Dropped Frames"] = self.dropped_frames
        state["Data Rate [MB/s]"] = data_rate
        state["Frame Rate [fps]"] = frame_rate
        self.log.info(
            f"id: {self.id}, "
            f"frame: {state['Frame Index']}, "
            f"input: {state['Input Buffer Size']}, "
            f"output: {state['Output Buffer Size']}, "
            f"dropped: {state['Dropped Frames']}, "
            f"data rate: {state['Data Rate [MB/s]']:.2f} [MB/s], "
            f"frame rate: {state['Frame Rate [fps]']:.2f} [fps]."
        )
        self.pre_frame_time = time.time()
        self.pre_frame_count_px = cap_info.nFrameCount

        return state

    def log_metadata(self):
        """
        Log all metadata from the camera to the logger.
        """

        # log dcam camera settings
        self.log.info("dcam camera parameters")
        idprop = self.dcam.prop_getnextid(0)
        while idprop is not False:
            propname = self.dcam.prop_getname(idprop)
            propvalue = self.dcam.prop_getvalue(idprop)
            self.log.info(f"{propname}, {propvalue}")
            idprop = self.dcam.prop_getnextid(idprop)

    def _update_parameters(self):
        """
        Internal function to update values for: \n
        - minimumum, maximum, and step values for settings \n
        - available binning modes \n
        - available pixel types \n
        - available trigger modes \n
        - available trigger sources \n
        - available trigger polarities \n
        - available sensor modes \n
        - available readout directions \n
        """

        # grab parameter values
        self._get_min_max_step_values()
        # check binning options
        self._query_binning()
        # check pixel type options
        self._query_pixel_types()
        # check trigger mode options
        self._query_trigger_modes()
        # check trigger source options
        self._query_trigger_sources()
        # check trigger polarity options
        self._query_trigger_polarities()
        # check sensor mode options
        self._query_sensor_modes()
        # check readout direction options
        self._query_readout_directions()

    def _get_min_max_step_values(self):
        """
        Internal function that queries camera SDK to determine \n
        minimum, maximumm, and step values.
        """
        # gather min max values
        # convert from s to ms
        self.min_exposure_time_ms = (
            self.dcam.prop_getattr(PROPERTIES["exposure_time"]).valuemin * 1e3
        )
        self.max_exposure_time_ms = (
            self.dcam.prop_getattr(PROPERTIES["exposure_time"]).valuemax * 1e3
        )
        # convert from s to us
        self.min_line_interval_us = (
            self.dcam.prop_getattr(PROPERTIES["line_interval"]).valuemin * 1e6
        )
        self.max_line_interval_us = (
            self.dcam.prop_getattr(PROPERTIES["line_interval"]).valuemax * 1e6
        )
        self.min_width_px = self.dcam.prop_getattr(PROPERTIES["image_width"]).valuemin
        self.max_width_px = self.dcam.prop_getattr(PROPERTIES["image_width"]).valuemax
        self.min_height_px = self.dcam.prop_getattr(PROPERTIES["image_height"]).valuemin
        self.max_height_px = self.dcam.prop_getattr(PROPERTIES["image_height"]).valuemax
        self.min_offset_x_px = self.dcam.prop_getattr(
            PROPERTIES["subarray_hpos"]
        ).valuemin
        self.max_offset_x_px = self.dcam.prop_getattr(
            PROPERTIES["subarray_hpos"]
        ).valuemax
        self.min_offset_y_px = self.dcam.prop_getattr(
            PROPERTIES["subarray_vpos"]
        ).valuemin
        self.max_offset_y_px = self.dcam.prop_getattr(
            PROPERTIES["subarray_vpos"]
        ).valuemax
        # convert from s to us
        self.step_exposure_time_ms = (
            self.dcam.prop_getattr(PROPERTIES["exposure_time"]).valuestep * 1e3
        )
        self.step_line_interval_us = (
            self.dcam.prop_getattr(PROPERTIES["line_interval"]).valuestep * 1e6
        )
        self.step_width_px = self.dcam.prop_getattr(PROPERTIES["image_width"]).valuestep
        self.step_height_px = self.dcam.prop_getattr(
            PROPERTIES["image_height"]
        ).valuestep
        self.step_offset_x_px = self.dcam.prop_getattr(
            PROPERTIES["subarray_hpos"]
        ).valuestep
        self.step_offset_y_px = self.dcam.prop_getattr(
            PROPERTIES["subarray_vpos"]
        ).valuestep

        self.log.debug(f"min exposure time is: {self.min_exposure_time_ms} ms")
        self.log.debug(f"max exposure time is: {self.max_exposure_time_ms} ms")
        self.log.debug(f"min line interval is: {self.min_line_interval_us} us")
        self.log.debug(f"max line interval is: {self.max_line_interval_us} us")
        self.log.debug(f"min width is: {self.min_width_px} px")
        self.log.debug(f"max width is: {self.max_width_px} px")
        self.log.debug(f"min height is: {self.min_height_px} px")
        self.log.debug(f"max height is: {self.max_height_px} px")
        self.log.debug(f"min offset x is: {self.min_offset_x_px} px")
        self.log.debug(f"max offset x is: {self.max_offset_x_px} px")
        self.log.debug(f"min offset y is: {self.min_offset_y_px} px")
        self.log.debug(f"max offset y is: {self.max_offset_y_px} px")
        self.log.debug(
            f"step exposure time is: \
                       {self.step_exposure_time_ms} ms"
        )
        self.log.debug(
            f"step line interval is: \
                       {self.step_line_interval_us} us"
        )
        self.log.debug(f"step width is: {self.step_width_px} px")
        self.log.debug(f"step height is: {self.step_height_px} px")
        self.log.debug(f"step offset x is: {self.step_offset_x_px} px")
        self.log.debug(f"step offset y is: {self.step_offset_y_px} px")

    def _query_trigger_modes(self):
        """
        Internal function that queries camera SDK to determine \n
        trigger mode options.
        """

        min_prop_value = int(
            self.dcam.prop_getattr(PROPERTIES["trigger_mode"]).valuemin
        )
        max_prop_value = int(
            self.dcam.prop_getattr(PROPERTIES["trigger_mode"]).valuemax
        )
        for prop_value in range(min_prop_value, max_prop_value + 1):
            reply = self.dcam.prop_getvaluetext(PROPERTIES["trigger_mode"], prop_value)
            if not reply:
                TRIGGERS["mode"][reply.lower()] = prop_value

    def _query_trigger_sources(self):
        """
        Internal function that queries camera SDK to determine \n
        trigger source options.
        """

        min_prop_value = int(
            self.dcam.prop_getattr(PROPERTIES["trigger_source"]).valuemin
        )
        max_prop_value = int(
            self.dcam.prop_getattr(PROPERTIES["trigger_source"]).valuemax
        )
        for prop_value in range(min_prop_value, max_prop_value + 1):
            reply = self.dcam.prop_getvaluetext(
                PROPERTIES["trigger_source"], prop_value
            )
            if not reply:
                TRIGGERS["source"][reply.lower()] = prop_value

    def _query_trigger_polarities(self):
        """
        Internal function that queries camera SDK to determine \n
        trigger polarity options.
        """

        min_prop_value = int(
            self.dcam.prop_getattr(PROPERTIES["trigger_polarity"]).valuemin
        )
        max_prop_value = int(
            self.dcam.prop_getattr(PROPERTIES["trigger_polarity"]).valuemax
        )
        for prop_value in range(min_prop_value, max_prop_value + 1):
            reply = self.dcam.prop_getvaluetext(
                PROPERTIES["trigger_polarity"], prop_value
            )
            if not reply:
                TRIGGERS["polarity"][reply.lower()] = prop_value

    def _query_sensor_modes(self):
        """
        Internal function that queries camera SDK to determine \n
        sensor mode options.
        """

        min_prop_value = int(self.dcam.prop_getattr(PROPERTIES["sensor_mode"]).valuemin)
        max_prop_value = int(self.dcam.prop_getattr(PROPERTIES["sensor_mode"]).valuemax)
        for prop_value in range(min_prop_value, max_prop_value + 1):
            reply = self.dcam.prop_getvaluetext(PROPERTIES["sensor_mode"], prop_value)
            if not reply:
                SENSOR_MODES[reply.lower()] = prop_value

    def _query_readout_directions(self):
        """
        Internal function that queries camera SDK to determine \n
        readout direction options.
        """

        min_prop_value = int(
            self.dcam.prop_getattr(PROPERTIES["readout_direction"]).valuemin
        )
        max_prop_value = int(
            self.dcam.prop_getattr(PROPERTIES["readout_direction"]).valuemax
        )
        for prop_value in range(min_prop_value, max_prop_value + 1):
            reply = self.dcam.prop_getvaluetext(
                PROPERTIES["readout_direction"], prop_value
            )
            if not reply:
                READOUT_DIRECTIONS[reply.lower()] = prop_value

    def _query_binning(self):
        """
        Internal function that queries camera SDK to determine \n
        binning options.
        """

        min_prop_value = int(self.dcam.prop_getattr(PROPERTIES["binning"]).valuemin)
        max_prop_value = int(self.dcam.prop_getattr(PROPERTIES["binning"]).valuemax)
        for prop_value in range(min_prop_value, max_prop_value + 1):
            reply = self.dcam.prop_getvaluetext(PROPERTIES["binning"], prop_value)
            if not reply:
                BINNING[reply.lower()] = prop_value

    def _query_pixel_types(self):
        """
        Internal function that queries camera SDK to determine \n
        pixel type options.
        """

        min_prop_value = int(self.dcam.prop_getattr(PROPERTIES["pixel_type"]).valuemin)
        max_prop_value = int(self.dcam.prop_getattr(PROPERTIES["pixel_type"]).valuemax)
        for prop_value in range(min_prop_value, max_prop_value + 1):
            reply = self.dcam.prop_getvaluetext(PROPERTIES["pixel_type"], prop_value)
            if not reply:
                PIXEL_TYPES[reply.lower()] = prop_value
