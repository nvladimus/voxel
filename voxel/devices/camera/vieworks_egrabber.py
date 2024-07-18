import logging
import numpy
from voxel.devices.camera.base import BaseCamera
from voxel.devices.camera.sdks.egrabber import *
from voxel.devices.utils.singleton import Singleton
from voxel.processes.gpu.gputools.downsample_2d import DownSample2D
from voxel.descriptors.deliminated_property import DeliminatedProperty

BUFFER_SIZE_MB = 2400

# generate valid binning by querying egrabber
# should be of the form
# {"2": "X2",
#  "3": "X3",
#  "4": "X4"...
# }
BINNING = dict()

# generate valid pixel types by querying egrabber
# should be of the form
# {"mono8": "Mono8",
#  "mono12": "Mono12",
#  "mono16": "Mono16"...
# }
PIXEL_TYPES = dict()

# generate line intervals by querying egrabber
# should be of the form
# {"mono8": 15.0,
#  "mono12": 25.5,
#  "mono16": 45.44 ...
# }
LINE_INTERVALS_US = dict()

# generate bit packing modes by querying egrabber
# should be of the form
# {"msb": "Msb",
#  "lsb": "Lsb",
#  "none": "None" ...
# }
BIT_PACKING_MODES = dict()

# generate triggers by querying egrabber
# should be of the form
# {"mode": {"on": "On",
#           "off": "Off"},
#  "source": {"software": "Software",
#             "line0": "Line0"},
#  "polarity": {"risingedge": "RisingEdge",
#               "fallingedge": "FallingEdge"}
# }
TRIGGERS = {"mode": dict(),
            "source": dict(),
            "polarity": dict()}


# singleton wrapper around EGenTL
class EGenTLSingleton(EGenTL, metaclass=Singleton):
    """
    Singleton wrapper around the eGrabber interface.
    """
    def __init__(self):
        super(EGenTLSingleton, self).__init__()


class Camera(BaseCamera):
    """
    Camera class for Vieworks camera using eGrabber SDK. \n

    :param id: The serial number ID of the camera
    :type id: str
    :rtype: Camera object
    """
    def __init__(self, id: str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # convert to string incase serial # is entered as int
        self.id = str(id)
        self.gentl = EGenTLSingleton()
        discovery = EGrabberDiscovery(self.gentl)
        discovery.discover()
        # list all possible grabbers
        egrabber_list = {'grabbers': []}
        interface_count = discovery.interface_count()
        for interfaceIndex in range(interface_count):
            device_count = discovery.device_count(interfaceIndex)
            for deviceIndex in range(device_count):
                if discovery.device_info(interfaceIndex,
                                         deviceIndex).deviceVendorName != '':
                    stream_count = discovery.stream_count(interfaceIndex,
                                                          deviceIndex)
                    for streamIndex in range(stream_count):
                        info = {'interface': interfaceIndex,
                                'device': deviceIndex,
                                'stream': streamIndex
                                }
                        egrabber_list['grabbers'].append(info)

        # for camera in discovery.cameras:
        del discovery

        # identify by serial number and return correct grabber
        if not egrabber_list['grabbers']:
            raise ValueError('no valid cameras found. \
                             check connections and close any software.')

        try:
            for egrabber in egrabber_list['grabbers']:
                grabber = EGrabber(self.gentl,
                                   egrabber['interface'],
                                   egrabber['device'],
                                   egrabber['stream'],
                                   remote_required=True)
                # note the framegrabber serial number is also available with:
                # grabber.interface.get('DeviceSerialNumber)
                if grabber.remote.get('DeviceSerialNumber') == self.id:
                    self.log.info(f"grabber found for S/N: {self.id}")
                    self.grabber = grabber
                    self.egrabber = egrabber
                    break
        except:
            self.log.error(f"no grabber found for S/N: {self.id}")
            raise ValueError(f"no grabber found for S/N: {self.id}")

        del grabber
        # initialize binning as 1
        self._binning = 1
        # initialize parameter values
        self._update_parameters()

    @DeliminatedProperty(minimum=lambda self: self.min_exposure_time_ms,
                         maximum=lambda self: self.max_exposure_time_ms)
    def exposure_time_ms(self):
        """
        Get the exposure time of the camera in ms.

        :return: The exposure time in ms.
        :rtype: float
        """
        # us to ms conversion
        return self.grabber.remote.get("ExposureTime")/1000

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float):
        """
        Set the exposure time of the camera in ms.

        :param exposure_time_ms: The exposure time in ms.
        :type exposure_time_ms: float
        :rtype: None
        """
        # Note: round ms to nearest us
        self.grabber.remote.set("ExposureTime",
                                round(exposure_time_ms * 1e3, 1))
        self.log.info(f"exposure time set to: {exposure_time_ms} ms")
        # refresh parameter values
        self._get_min_max_step_values()

    @DeliminatedProperty(minimum=lambda self: self.min_width_px,
                         maximum=lambda self: self.max_width_px)
    def width_px(self):
        """
        Get the width of the camera region of interest in pixels.

        :return: The width of the region of interest in pixels.
        :rtype: int
        """
        return self.grabber.remote.get("Width")
    
    @width_px.setter
    def width_px(self, value: int):
        """
        Set the width of the camera region of interest in pixels.

        :param value: The width of the region of interest in pixels.
        :type value: int
        :rtype: None
        """
        # reset offset to (0,0)
        self.grabber.remote.set("OffsetX", 0)
        centered_offset_px = round((self.max_width_px / 2 - value / 2)
                                   / self.step_width_px) * self.step_width_px
        self.grabber.remote.set("OffsetX", centered_offset_px)
        self.grabber.remote.set("Width", value)
        self.log.info(f"width set to: {value} px")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def width_offset_px(self):
        """
        Get the width offset of the camera region of interest in pixels.

        :return: The width offset of the region of interest in pixels.
        :rtype: int
        """
        return self.grabber.remote.get("OffsetX")

    @DeliminatedProperty(minimum=lambda self: self.min_height_px,
                         maximum=lambda self: self.max_height_px)
    def height_px(self):
        """
        Get the height of the camera region of interest in pixels.

        :return: The height of the region of interest in pixels.
        :rtype: int
        """
        return self.grabber.remote.get("Height")

    @height_px.setter
    def height_px(self, value: int):
        """
        Set the height of the camera region of interest in pixels.

        :param value: The height of the region of interest in pixels.
        :type value: int
        :rtype: None
        """
        # reset offset to (0,0)
        self.grabber.remote.set("OffsetY", 0)
        centered_offset_px = round((self.max_height_px / 2 - value / 2)
                                   / self.step_height_px) * self.step_height_px
        self.grabber.remote.set("OffsetY", centered_offset_px)
        self.grabber.remote.set("Height", value)
        self.log.info(f"height set to: {value} px")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def height_offset_px(self):
        """
        Get the height offset of the camera region of interest in pixels.

        :return: The height offset of the region of interest in pixels.
        :rtype: int
        """
        return self.grabber.remote.get("OffsetY")

    @property
    def pixel_type(self):
        """
        Get the pixel type of the camera.

        :return: The pixel type of the camera.
        :rtype: str
        """
        pixel_type = self.grabber.remote.get("PixelFormat")
        # invert the dictionary and find the abstracted key to output
        return next(key for key, value in
                    PIXEL_TYPES.items() if
                    value == pixel_type)

    @pixel_type.setter
    def pixel_type(self, pixel_type_bits: str):
        """
        The pixel type of the camera: \n
        - mono8, mono10, mono12, mono14, mono16, etc.

        :param pixel_type_bits: The pixel type
        :type pixel_type_bits: str
        :rtype: None
        """
        valid = list(PIXEL_TYPES.keys())
        if pixel_type_bits not in valid:
            raise ValueError("pixel_type_bits must be one of %r." % valid)
        # note: for the Vieworks VP-151MX camera
        # the pixel type also controls line interval
        self.grabber.remote.set("PixelFormat", PIXEL_TYPES[pixel_type_bits])
        self.log.info(f"pixel type set to: {pixel_type_bits}")
        # refresh parameter values
        self._update_parameters()

    @property
    def bit_packing_mode(self):
        """
        Get the bit packing mode of the camera.

        :return: The bit packing mode of the camera.
        :rtype: str
        """
        bit_packing = self.grabber.stream.get("UnpackingMode")
        # invert the dictionary and find the abstracted key to output
        return next(key for key, value in
                    BIT_PACKING_MODES.items()
                    if value == bit_packing)

    @bit_packing_mode.setter
    def bit_packing_mode(self, bit_packing: str):
        """
        The bit packing mode of the camera: \n
        - lsb, msb, none

        :param bit_packing: The bit packing mode
        :type bit_packing: str
        :rtype: None
        """
        valid = list(BIT_PACKING_MODES.keys())
        if bit_packing not in valid:
            raise ValueError("bit_packing_mode must be one of %r." % valid)
        self.grabber.stream.set("UnpackingMode",
                                BIT_PACKING_MODES[bit_packing])
        self.log.info(f"bit packing mode set to: {bit_packing}")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def line_interval_us(self):
        """
        Get the line interval of the camera in us. \n
        This is the time interval between adjacnet \n
        rows activating on the camera sensor.

        :return: The line interval of the camera in us
        :rtype: float
        """
        pixel_type = self.pixel_type
        return LINE_INTERVALS_US[pixel_type]

    @property
    def frame_time_ms(self):
        """
        Get the frame time of the camera in ms. \n
        This is the total time to acquire a single image

        :return: The frame time of the camera in ms
        :rtype: float
        """
        return (self.line_interval_us * self.height_px)/1000 \
            + self.exposure_time_ms

    @property
    def trigger(self):
        """
        Get the trigger mode of the camera. \n
        The trigger mode consists of three parameters: \n
        - mode (e.g. on or off) \n
        - source (e.g. internal or external) \n
        - polarity (e.g. rising edge or falling edge)

        :return: The trigger mode of the camera.
        :rtype: dict
        """
        mode = self.grabber.remote.get("TriggerMode")
        source = self.grabber.remote.get("TriggerSource")
        polarity = self.grabber.remote.get("TriggerActivation")
        return {"mode": next(key for key, value in
                             TRIGGERS['mode'].items()
                             if value == mode),
                "source": next(key for key, value in
                               TRIGGERS['source'].items()
                               if value == source),
                "polarity": next(key for key, value in
                                 TRIGGERS['polarity'].items()
                                 if value == polarity)}

    @trigger.setter
    def trigger(self, trigger: dict):
        """
        Set the trigger mode of the camera. \n
        The trigger mode consists of three parameters: \n
        - mode (e.g. on or off) \n
        - source (e.g. internal or external) \n
        - polarity (e.g. rising edge or falling edge)

        :param trigger: The trigger mode of the camera
        :type trigger: dict
        :rtype: None
        """
        mode = trigger['mode']
        source = trigger['source']
        polarity = trigger['polarity']
        valid_mode = list(TRIGGERS['mode'].keys())
        if mode not in valid_mode:
            raise ValueError("mode must be one of %r." % valid_mode)
        valid_source = list(TRIGGERS['source'].keys())
        if source not in valid_source:
            raise ValueError("source must be one of %r." % valid_source)
        valid_polarity = list(TRIGGERS['polarity'].keys())
        if polarity not in valid_polarity:
            raise ValueError("polarity must be one of %r." % valid_polarity)
        # note: Setting TriggerMode if it's already correct will throw an error
        if self.grabber.remote.get("TriggerMode") != mode:
            # set camera to external trigger mode
            self.grabber.remote.set("TriggerMode", TRIGGERS['mode'][mode])
        self.grabber.remote.set("TriggerSource", TRIGGERS['source'][source])
        self.grabber.remote.set("TriggerActivation",
                                TRIGGERS['polarity'][polarity])
        self.log.info(f"trigger set to, mode: {mode}, source: {source}, \
                      polarity: {polarity}")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def binning(self):
        """
        Get the binning mode of the camera. \n
        Integer value, e.g. 2 is 2x2 binning

        :return: The binning mode of the camera
        :rtype: int
        """
        return self._binning

    @binning.setter
    def binning(self, binning: int):
        """
        Set the binning of the camera. \n
        If the binning is not supported in hardware \n
        it will be implemented via software using the GPU. \n
        This API assumes identical binning in X and Y.

        :param binning: The binning mode of the camera.
        :type binning: int
        :rtype: None
        """
        valid_binning = list(BINNING.keys())
        if binning not in valid_binning:
            raise ValueError("binning must be one of %r." % valid_binning)
        self._binning = binning
        # if binning is not an integer, do it in hardware
        if not isinstance(BINNING[binning], int):
            self.grabber.remote.set("BinningHorizontal", BINNING[binning])
            self.grabber.remote.set("BinningVertical", BINNING[binning])
        # initialize the opencl binning program
        else:
            self.gpu_binning = DownSample2D(binning=int(self._binning))
        # refresh parameter values
        self._get_min_max_step_values()

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
        return self.max_height_px

    @property
    def signal_mainboard_temperature_c(self):
        """
        Get the mainboard temperature of the camera in deg C.

        :return: The mainboard temperature of the camera in deg C.
        :rtype: float
        """
        self.grabber.remote.set("DeviceTemperatureSelector", "Mainboard")
        state = {}
        state['Sensor Temperature [C]'] = \
            self.grabber.remote.get("DeviceTemperature")
        return state

    @property
    def signal_sensor_temperature_c(self):
        """
        Get the sensor temperature of the camera in deg C.

        :return: The sensor temperature of the camera in deg C.
        :rtype: float
        """
        self.grabber.remote.set("DeviceTemperatureSelector", "Sensor")
        state = {}
        state['Sensor Temperature [C]'] = \
            self.grabber.remote.get("DeviceTemperature")
        return state

    def prepare(self):
        """
        Prepare the camera to acquire images. \n
        Initializes the camera buffer.

        rtype: None
        """
        # determine bits to bytes
        if self.pixel_type == 'mono8':
            bit_to_byte = 1
        else:
            bit_to_byte = 2
        # software binning, so frame size is independent of binning factor
        frame_size_mb = self.width_px*self.height_px*bit_to_byte/1e6
        self.buffer_size_frames = round(BUFFER_SIZE_MB / frame_size_mb)
        # realloc buffers appears to be allocating
        # ram on the pc side, not camera side.
        # allocate RAM buffer N frames
        self.grabber.realloc_buffers(self.buffer_size_frames)
        self.log.info(f"buffer set to: {self.buffer_size_frames} frames")

    def start(self, frame_count: int=GENTL_INFINITE):
        """
        Start the camera to acquire a certain number of frames. \n
        If frame number is not specified, acquires infinitely until stopped. \n
        Initializes the camera buffer.

        :param frame_count: The number of frames to acquire
        :type frame_count: int
        :rtype: None
        """
        if frame_count == float('inf'):
            frame_count = GENTL_INFINITE
        self.grabber.start(frame_count=frame_count)

    def stop(self):
        """
        Stop the camera.

        rtype: None
        """
        self.grabber.stop()

    def abort(self):
        """
        Abort the camera.

        rtype: None
        """
        self.stop()

    def close(self):
        """
        Close the camera.

        rtype: None
        """
        del self.grabber

    def reset(self):
        """
        Reset the camera.

        rtype: None
        """
        del self.grabber
        self.grabber = EGrabber(self.gentl,
                                self.egrabber['interface'],
                                self.egrabber['device'],
                                self.egrabber['stream'],
                                remote_required=True)

    def grab_frame(self):
        """
        Grab a frame from the camera buffer. \n
        If binning is via software, the GPU binned \n
        image is computed and returned.

        :return: The camera frame of size (height, width).
        :rtype: numpy.array
        """
        # Note: creating the buffer and then "pushing" it at the end has the
        #   effect of moving the internal camera frame buffer from the output
        #   pool back to the input pool, so it can be reused.
        column_count = self.grabber.remote.get("Width")
        row_count = self.grabber.remote.get("Height")
        timeout_ms = 1000
        with Buffer(self.grabber, timeout=timeout_ms) as buffer:
            ptr = buffer.get_info(BUFFER_INFO_BASE, INFO_DATATYPE_PTR)  # grab pointer to new frame
            # grab frame data
            data = ct.cast(ptr, ct.POINTER(ct.c_ubyte * column_count * row_count * 2)).contents
            # cast data to numpy array of correct size/datatype:
            image = numpy.frombuffer(data, count=int(column_count * row_count),
                                     dtype=numpy.uint16).reshape((row_count,
                                                                  column_count))
        # do software binning if != 1 and not a string for setting in egrabber
        if self._binning > 1 and isinstance(self._binning, int):
            return self.gpu_binning.run(image)
        else:
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
        # Detailed description of constants here:
        # https://documentation.euresys.com/Products/Coaxlink/Coaxlink/en-us/Content/IOdoc/egrabber-reference/
        # namespace_gen_t_l.html#a6b498d9a4c08dea2c44566722699706e
        state = {}
        state['Frame Index'] = self.grabber.stream.get_info(STREAM_INFO_NUM_DELIVERED, INFO_DATATYPE_SIZET)
        state['Input Buffer Size'] = self.grabber.stream.get_info(STREAM_INFO_NUM_QUEUED,
                                                               INFO_DATATYPE_SIZET)
        state['Output Buffer Size'] = self.grabber.stream.get_info(STREAM_INFO_NUM_AWAIT_DELIVERY,
                                                                INFO_DATATYPE_SIZET)
        # number of underrun, i.e. dropped frames
        state['Dropped Frames'] = self.grabber.stream.get_info(STREAM_INFO_NUM_UNDERRUN,
                                                               INFO_DATATYPE_SIZET)
        # adjust data rate based on internal software binning
        state['Data Rate [MB/s]'] = self.grabber.stream.get('StatisticsDataRate')/self._binning**2
        state['Frame Rate [fps]'] = self.grabber.stream.get('StatisticsFrameRate')
        self.log.info(f"id: {self.id}, "
                      f"frame: {state['Frame Index']}, "
                      f"input: {state['Input Buffer Size']}, "
                      f"output: {state['Output Buffer Size']}, "
                      f"dropped: {state['Dropped Frames']}, "
                      f"data rate: {state['Data Rate [MB/s]']:.2f} [MB/s], "
                      f"frame rate: {state['Frame Rate [fps]']:.2f} [fps].")
        return state

    def log_metadata(self):
        """
        Log all metadata from the camera to the logger.

        :rtype: None
        """
        # log egrabber camera settings
        self.log.info('egrabber camera parameters')
        categories = self.grabber.device.get(query.categories())
        for category in categories:
            features = self.grabber.device.get(query.features_of(category))
            for feature in features:
                if self.grabber.device.get(query.available(feature)):
                    if self.grabber.device.get(query.readable(feature)):
                        if not self.grabber.device.get(query.command(feature)):
                            self.log.info(f'device, {feature}, {self.grabber.device.get(feature)}')

        categories = self.grabber.remote.get(query.categories())
        for category in categories:
            features = self.grabber.remote.get(query.features_of(category))
            for feature in features:
                if self.grabber.remote.get(query.available(feature)):
                    if self.grabber.remote.get(query.readable(feature)):
                        if not self.grabber.remote.get(query.command(feature)):
                            if feature != "BalanceRatioSelector" and feature != "BalanceWhiteAuto":
                                self.log.info(f'remote, {feature}, {self.grabber.remote.get(feature)}')

        categories = self.grabber.stream.get(query.categories())
        for category in categories:
            features = self.grabber.stream.get(query.features_of(category))
            for feature in features:
                if self.grabber.stream.get(query.available(feature)):
                    if self.grabber.stream.get(query.readable(feature)):
                        if not self.grabber.stream.get(query.command(feature)):
                            self.log.info(f'stream, {feature}, {self.grabber.stream.get(feature)}')

        categories = self.grabber.interface.get(query.categories())
        for category in categories:
            features = self.grabber.interface.get(query.features_of(category))
            for feature in features:
                if self.grabber.interface.get(query.available(feature)):
                    if self.grabber.interface.get(query.readable(feature)):
                        if not self.grabber.interface.get(query.command(feature)):
                            self.log.info(f'interface, {feature}, {self.grabber.interface.get(feature)}')

        categories = self.grabber.system.get(query.categories())
        for category in categories:
            features = self.grabber.system.get(query.features_of(category))
            for feature in features:
                if self.grabber.system.get(query.available(feature)):
                    if self.grabber.system.get(query.readable(feature)):
                        if not self.grabber.system.get(query.command(feature)):
                            self.log.info(f'system, {feature}, {self.grabber.system.get(feature)}')

    def _update_parameters(self):
        """
        Internal function to update values for: \n
        - minimumum, maximum, and step values for settings \n
        - available binning modes \n
        - available pixel types \n
        - available bit packing modes \n
        - available trigger modes \n
        - available trigger sources \n
        - available trigger polarities \n

        :rtype: None
        """
        # grab min/max parameter values
        self._get_min_max_step_values()
        # check binning options
        self._query_binning()
        # check pixel types options
        self._query_pixel_types()
        # check bit packing options
        self._query_bit_packing_modes()
        # check trigger mode options
        self._query_trigger_modes()
        # check trigger source options
        self._query_trigger_sources()
        # check trigger polarity options
        self._query_trigger_polarities()

    def _get_min_max_step_values(self):
        """
        Internal function that queries camera SDK to determine \n
        minimum, maximumm, and step values.

        :rtype: None
        """
        # gather min max values. all may not be available for certain cameras.
        # minimum exposure time
        # convert from us to ms
        try:
            self.min_exposure_time_ms = \
                self.grabber.remote.get("ExposureTime.Min")/1e3
            type(self).exposure_time_ms.minimum = self.min_exposure_time_ms
            self.log.debug(f"min exposure time is: \
                           {self.min_exposure_time_ms} ms")
        except:
            self.log.debug(f"min exposure time not \
                           available for camera {self.id}")
        # maximum exposure time
        # convert from us to ms
        try:
            self.max_exposure_time_ms = \
                self.grabber.remote.get("ExposureTime.Max")/1e3
            type(self).exposure_time_ms.maximum = self.max_exposure_time_ms
            self.log.debug(f"max exposure time is: \
                           {self.max_exposure_time_ms} ms")
        except:
            self.log.debug(f"max exposure time not \
                           available for camera {self.id}")
        # minimum width
        try:
            self.min_width_px = self.grabber.remote.get("Width.Min")
            type(self).width_px.minimum = self.min_width_px
            self.log.debug(f"min width is: {self.min_width_px} px")
        except:
            self.log.debug(f"min width not available for camera {self.id}")
        # maximum width
        try:
            self.max_width_px = self.grabber.remote.get("Width.Max")
            type(self).width_px.maximum = self.max_width_px
            self.log.debug(f"max width is: {self.max_width_px} px")
        except:
            self.log.debug(f"max width not available for camera {self.id}")
        # minimum height
        try:
            self.min_height_px = self.grabber.remote.get("Height.Min")
            type(self).height_px.minimum = self.min_height_px
            self.log.debug(f"min height is: {self.min_height_px} px")
        except:
            self.log.debug(f"min height not available for camera {self.id}")
        # maximum height
        try:
            self.max_height_px = self.grabber.remote.get("Height.Max")
            type(self).height_px.maximum = self.max_height_px
            self.log.debug(f"max height is: {self.max_height_px} px")
        except:
            self.log.debug(f"max height not available for camera {self.id}")
        # minimum offset x
        try:
            self.min_offset_x_px = self.grabber.remote.get("OffsetX.Min")
            self.log.debug(f"min offset x is: {self.min_offset_x_px} px")
        except:
            self.log.debug(f"min offset x not available for camera {self.id}")
        # maximum offset x
        try:
            self.max_offset_x_px = self.grabber.remote.get("OffsetX.Max")
            self.log.debug(f"max offset x is: {self.max_offset_x_px} px")
        except:
            self.log.debug(f"max offset x not available for camera {self.id}")
        # minimum offset y
        try:
            self.min_offset_y_px = self.grabber.remote.get("OffsetY.Min")
            self.log.debug(f"min offset y is: {self.min_offset_y_px} px")
        except:
            self.log.debug(f"min offset y not available for camera {self.id}")
        # maximum offset y
        try:
            self.max_offset_y_px = self.grabber.remote.get("OffsetY.Max")
            self.log.debug(f"max offset y is: {self.max_offset_y_px} px")
        except:
            self.log.debug(f"max offset y not available for camera {self.id}")
        # step exposure time
        # convert from us to ms
        try:
            self.step_exposure_time_ms = \
                self.grabber.remote.get("ExposureTime.Inc")/1e3
            type(self).exposure_time_ms.step = self.step_exposure_time_ms
            self.log.debug(f"step exposure time is: \
                           {self.step_exposure_time_ms} ms")
        except:
            self.log.debug(f"step exposure time not \
                            available for camera {self.id}")
        # step width
        try:
            self.step_width_px = self.grabber.remote.get("Width.Inc")
            type(self).width_px.step = self.step_width_px
            self.log.debug(f"step width is: {self.step_width_px} px")
        except:
            self.log.debug(f"step width not available for camera {self.id}")
        # step height
        try:
            self.step_height_px = self.grabber.remote.get("Height.Inc")
            type(self).height_px.step = self.step_height_px
            self.log.debug(f"step height is: {self.step_height_px} px")
        except:
            self.log.debug(f"step height not available for camera {self.id}")
        # step offset x
        try:
            self.step_offset_x_px = self.grabber.remote.get("OffsetX.Inc")
            self.log.debug(f"step offset x is: {self.step_offset_x_px} px")
        except:
            self.log.debug(f"step offset x not available for camera {self.id}")
        # step offset y
        try:
            self.step_offset_y_px = self.grabber.remote.get("OffsetY.Inc")
            self.log.debug(f"step offset y is: {self.step_offset_y_px} px")
        except:
            self.log.debug(f"step offset y not available for camera {self.id}")

    def _query_binning(self):
        """
        Internal function that queries camera SDK to determine \n
        binning options.

        :rtype: None
        """
        # egrabber defines 1 as 'X1', 2 as 'X2', 3 as 'X3'...
        # check only horizontal since we will use same binning for vertical
        binning_options = self.grabber.remote.get("@ee BinningHorizontal",
                                                  dtype=list)
        init_binning = self.grabber.remote.get("BinningHorizontal")
        for binning in binning_options:
            try:
                self.grabber.remote.set("BinningHorizontal", binning)
                # generate integer key
                key = int(binning.replace("X", ""))
                BINNING[key] = binning
            except:
                self.log.debug(f"{binning} not avaiable on this camera")
                # only implement software binning for even numbers
                if int(binning.replace("X", "")) % 2 == 0:
                    self.log.debug(f"{binning} will be \
                                   implemented through software")
                    key = int(binning.replace("X", ""))
                    BINNING[key] = key
        # reset to initial value
        self.grabber.remote.set("BinningHorizontal", init_binning)

    def _query_pixel_types(self):
        """
        Internal function that queries camera SDK to determine \n
        pixel type options.

        :rtype: None
        """
        # egrabber defines as 'Mono8', 'Mono12', 'Mono16'...
        pixel_type_options = self.grabber.remote.get("@ee PixelFormat",
                                                     dtype=list)
        init_pixel_type = self.grabber.remote.get("PixelFormat")
        for pixel_type in pixel_type_options:
            try:
                self.grabber.remote.set("PixelFormat", pixel_type)
                # generate lowercase string key
                key = pixel_type.lower()
                PIXEL_TYPES[key] = pixel_type
            except:
                self.log.debug(f"{pixel_type} not avaiable on this camera")

        # once the pixel types are found, determine line intervals
        self._query_line_intervals()
        # reset to initial value
        self.grabber.remote.set("PixelFormat", init_pixel_type)

    def _query_bit_packing_modes(self):
        """
        Internal function that queries camera SDK to determine \n
        bit packing mode options.

        :rtype: None
        """
        # egrabber defines as 'Msb', 'Lsb', 'None'...
        bit_packing_options = self.grabber.stream.get("@ee UnpackingMode",
                                                      dtype=list)
        init_bit_packing = self.grabber.stream.get("UnpackingMode")
        for bit_packing in bit_packing_options:
            try:
                self.grabber.stream.set("UnpackingMode", bit_packing)
                # generate lowercase string key
                key = bit_packing.lower()
                BIT_PACKING_MODES[key] = bit_packing
            except:
                self.log.debug(f"{bit_packing} not avaiable on this camera")
        # reset to initial value
        self.grabber.stream.set("UnpackingMode", init_bit_packing)

    def _query_line_intervals(self):
        """
        Internal function that queries camera SDK to determine \n
        camera line interval. There is a camera specific number of \n
        inactive rows to account for. This is currently only added for \n
        the Vieworks VP-151MX camera. Other cameras need to be manually \n
        added.

        :rtype: None
        """
        # based on framerate and number of sensor rows
        for key in PIXEL_TYPES:
            # set pixel type
            self.grabber.remote.set("PixelFormat", PIXEL_TYPES[key])
            # check max acquisition rate, used to determine line interval
            max_frame_rate = self.grabber.remote.get("AcquisitionFrameRate.Max")
            # vp-151mx camera uses the sony imx411 camera
            # which has 10640 active rows but 10802 total rows.
            # from the manual 10760 are used during readout
            if self.grabber.remote.get("DeviceModelName") == "VP-151MX-M6H0":
                line_interval_s = (1 / max_frame_rate) \
                    / (self.sensor_height_px + 120)
            else:
                line_interval_s = (1 / max_frame_rate) \
                    / self.sensor_height_px
            # conver from s to us and store
            LINE_INTERVALS_US[key] = line_interval_s*1e6

    def _query_trigger_modes(self):
        """
        Internal function that queries camera SDK to determine \n
        trigger mode options.

        :rtype: None
        """
        trigger_mode_options = self.grabber.remote.get("@ee TriggerMode", dtype=list)
        init_trigger_mode = self.grabber.remote.get("TriggerMode")
        for trigger_mode in trigger_mode_options:
            # note: setting TriggerMode to the already set value throws an error
            # so check the current value and only set if new value
            if self.grabber.remote.get("TriggerMode") != trigger_mode:  # set camera to external trigger mode
                try:
                    self.grabber.remote.set("TriggerMode", trigger_mode)
                    # generate lowercase string key
                    key = trigger_mode.lower()
                    TRIGGERS['mode'][key] = trigger_mode
                except:
                    self.log.debug(f"{trigger_mode} not avaiable on this camera")
            # if it is already set to this value, we know that it is a valid setting
            else:
                key = trigger_mode.lower()
                print(key)
                TRIGGERS['mode'][key] = trigger_mode  
        # reset to initial value
        self.grabber.remote.set("TriggerMode", init_trigger_mode)

    def _query_trigger_sources(self):
        """
        Internal function that queries camera SDK to determine \n
        trigger source options.

        :rtype: None
        """
        trigger_source_options = self.grabber.remote.get("@ee TriggerSource", dtype=list)
        init_trigger_source = self.grabber.remote.get("TriggerSource")
        for trigger_source in trigger_source_options:
            try:
                self.grabber.remote.set("TriggerSource", trigger_source)
                # generate lowercase string key
                key = trigger_source.lower()
                TRIGGERS['source'][key] = trigger_source
            except:
                self.log.debug(f"{trigger_source} not avaiable on this camera") 
        # reset to initial value
        self.grabber.remote.set("TriggerSource", init_trigger_source)

    def _query_trigger_polarities(self):
        """
        Internal function that queries camera SDK to determine \n
        trigger polarity options.

        :rtype: None
        """
        trigger_polarity_options \
            = self.grabber.remote.get("@ee TriggerActivation", dtype=list)
        init_trigger_polarity = self.grabber.remote.get("TriggerActivation")
        for trigger_polarity in trigger_polarity_options:
            try:
                self.grabber.remote.set("TriggerActivation", trigger_polarity)
                # generate lowercase string key
                key = trigger_polarity.lower()
                TRIGGERS['polarity'][key] = trigger_polarity
            except:
                self.log.debug(f"{trigger_polarity} not \
                               avaiable on this camera")
        # reset to initial value
        self.grabber.remote.set("TriggerActivation", init_trigger_polarity)
