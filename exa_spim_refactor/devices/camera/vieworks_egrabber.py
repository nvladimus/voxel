import logging
import numpy
from functools import wraps
from base import BaseCamera
from singleton import Singleton
from egrabber import *

BUFFER_SIZE_MB = 2400

# generate valid binning by querying egrabber
BINNING = dict()

# generate valid pixel types by querying egrabber
PIXEL_TYPES = dict()

# generate line intervals by querying egrabber
LINE_INTERVALS_US = dict()

BIT_PACKING_MODES = {
    "msb": "Msb",
    "lsb": "Lsb",
    "none": "None"
}

TRIGGERS = {
    "modes": {
        "on": "On",
        "off": "Off",
    },
    "sources": {
        "internal": "None",
        "external": "Line0",
    },
    "polarity": {
        "rising": "RisingEdge",
        "falling": "FallingEdge",
    }
}

# singleton wrapper around EGenTL
class EGenTLSingleton(EGenTL, metaclass=Singleton):
    def __init__(self):
        super(EGenTLSingleton, self).__init__()

class Camera(BaseCamera):

    def __init__(self, id=str):
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.id = id
        gentl = EGenTLSingleton()
        discovery = EGrabberDiscovery(gentl)
        discovery.discover()
        # list all possible grabbers
        egrabber_list = {'grabbers': []}
        interface_count = discovery.interface_count()
        for interfaceIndex in range(interface_count):
            device_count = discovery.device_count(interfaceIndex)
            for deviceIndex in range(device_count):
                stream_count = discovery.stream_count(interfaceIndex, deviceIndex)
                for streamIndex in range(stream_count):
                    info = {'interface': interfaceIndex,
                            'device': deviceIndex,
                            'stream': streamIndex
                            }
                    egrabber_list['grabbers'].append(info)
        del discovery
        # identify by serial number and return correct grabber
        if not egrabber_list['grabbers']:
            raise ValueError('no valid cameras found. check connections and close any software.')

        for egrabber in egrabber_list['grabbers']:
            try:
                grabber = EGrabber(gentl, egrabber['interface'], egrabber['device'], egrabber['stream'],
                                   remote_required=True)
                if grabber.remote.get('DeviceSerialNumber') == self.id:
                    self.log.info(f"grabber found for S/N: {self.id}")
                    self.grabber = grabber
                    break
            except:
                self.log.error(f"no grabber found for S/N: {self.id}")
                raise ValueError(f"no grabber found for S/N: {self.id}")
        del grabber
        # initialize binning as 1
        self._binning = 1
        # grab min/max parameter values
        self._get_min_max_step_values()
        # check binning options
        self._query_binning()
        # check pixel types options
        self._query_pixel_types()

    @property
    def exposure_time_ms(self):
        # us to ms conversion
        return self.grabber.remote.get("ExposureTime")/1000

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float):

        if exposure_time_ms < self.min_exposure_time_ms or \
                exposure_time_ms > self.max_exposure_time_ms:
            self.log.error(f"exposure time must be >{self.min_exposure_time_ms} ms \
                             and <{self.max_exposure_time_ms} ms")
            raise ValueError(f"exposure time must be >{self.min_exposure_time_ms} ms \
                             and <{self.max_exposure_time_ms} ms")

        # Note: round ms to nearest us
        self.grabber.remote.set("ExposureTime", round(exposure_time_ms * 1e3, 1))
        self.log.info(f"exposure time set to: {exposure_time_ms} ms")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def roi(self):
        return {'width_px': self.grabber.remote.get("Width"),
                'height_px': self.grabber.remote.get("Height"),
                'width_offset_px': self.grabber.remote.get("OffsetX"),
                'height_offest_px': self.grabber.remote.get("OffsetY")}

    @roi.setter
    def roi(self, roi: dict):

        # reset roi to (0,0)
        self.grabber.remote.set("OffsetX", 0)
        self.grabber.remote.set("OffsetY", 0)
        # refresh parameter values
        self._get_min_max_step_values()

        width_px = roi['width_px']
        height_px = roi['height_px']

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

        self.grabber.remote.set("OffsetX", 0)
        self.grabber.remote.set("Width", width_px)
        # width offset must be a multiple of the divisible width in px
        centered_width_offset_px = round((self.max_width_px / 2 - width_px / 2) / self.step_width_px) * self.step_width_px
        self.grabber.remote.set("OffsetX", centered_width_offset_px)
        self.grabber.remote.set("OffsetY", 0)
        self.grabber.remote.set("Height", height_px)
        height_px = self.grabber.remote.get("Height")
        # Height offset must be a multiple of the divisible height in px
        centered_height_offset_px = round(
            (self.max_height_px / 2 - height_px / 2) / self.step_height_px) * self.step_height_px
        self.grabber.remote.set("OffsetY", centered_height_offset_px)
        self.log.info(f"roi set to: {width_px} x {height_px} [width x height]")
        self.log.info(f"roi offset set to: {centered_width_offset_px} x {centered_height_offset_px} [width x height]")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def pixel_type(self):
        pixel_type = self.grabber.remote.get("PixelFormat")
        # invert the dictionary and find the abstracted key to output
        return next(key for key, value in PIXEL_TYPES.items() if value == pixel_type)

    @pixel_type.setter
    def pixel_type(self, pixel_type_bits: str):

        valid = list(PIXEL_TYPES.keys())
        if pixel_type_bits not in valid:
            raise ValueError("pixel_type_bits must be one of %r." % valid)

        # Note: for the Vieworks VP-151MX camera, the pixel type also controls line interval
        self.grabber.remote.set("PixelFormat", PIXEL_TYPES[pixel_type_bits])
        self.log.info(f"pixel type set to: {pixel_type_bits}")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def bit_packing_mode(self):
        bit_packing = self.grabber.stream.get("UnpackingMode")
        # invert the dictionary and find the abstracted key to output
        return next(key for key, value in BIT_PACKING_MODES.items() if value == bit_packing)

    @bit_packing_mode.setter
    def bit_packing_mode(self, bit_packing: str):

        valid = list(BIT_PACKING_MODES.keys())
        if bit_packing not in valid:
            raise ValueError("bit_packing_mode must be one of %r." % valid)

        self.grabber.stream.set("UnpackingMode", BIT_PACKING_MODES[bit_packing])
        self.log.info(f"bit packing mode set to: {bit_packing}")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def line_interval_us(self):
        pixel_type = self.pixel_type
        return LINE_INTERVALS_US[pixel_type]

    @property
    def trigger(self):
        mode = self.grabber.remote.get("TriggerMode")
        source = self.grabber.remote.get("TriggerSource")
        polarity = self.grabber.remote.get("TriggerActivation")
        return {"mode": next(key for key, value in TRIGGERS['modes'].items() if value == mode),
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

        # Note: Setting TriggerMode if it's already correct will throw an error
        if self.grabber.remote.get("TriggerMode") != mode:  # set camera to external trigger mode
            self.grabber.remote.set("TriggerMode", TRIGGERS['modes'][mode])
        self.grabber.remote.set("TriggerSource", TRIGGERS['sources'][source])
        self.grabber.remote.set("TriggerActivation", TRIGGERS['polarity'][polarity])
        self.log.info(f"trigger set to, mode: {mode}, source: {source}, polarity: {polarity}")
        # refresh parameter values
        self._get_min_max_step_values()

    @property
    def binning(self):
        return next(key for key, value in BINNING.items() if value == self._binning)

    @binning.setter
    def binning(self, binning: str):
        valid_binning = list(BINNING.keys())
        if binning not in valid_binning:
            raise ValueError("binning must be one of %r." % valid_binning)
        self._binning = binning
        # if binning is not an integer, do it in hardware
        if not isinstance(BINNING[binning], int):
            self.grabber.remote.set("BinningHorizontal", self._binning)
            self.grabber.remote.set("BinningVertical", self._binning)

    @property
    def sensor_width_px(self):
        return self.max_width_px

    @property
    def sensor_height_px(self):
        return self.max_height_px

    @property
    def signal_mainboard_temperature_c(self):
        """get the mainboard temperature in degrees C."""
        self.grabber.remote.set("DeviceTemperatureSelector", "Mainboard")
        state = {}
        state['Sensor Temperature [C]'] = self.grabber.remote.get("DeviceTemperature")
        return state

    @property
    def signal_sensor_temperature_c(self):
        """get the sensor temperature in degrees C."""
        self.grabber.remote.set("DeviceTemperatureSelector", "Sensor")
        state = {}
        state['Sensor Temperature [C]'] = self.grabber.remote.get("DeviceTemperature")
        return state

    @property
    def readout_mode(self):
        self.log.warning(f"binning is not available with egrabber")
        readout_mode = "light sheet forward"
        return readout_mode

    def prepare(self):
        # determine bits to bytes
        if self.pixel_type == 'mono8':
            bit_to_byte = 1
        else:
            bit_to_byte = 2
        # software binning, so frame size is independent of binning factor
        frame_size_mb = self.roi['width_px']*self.roi['height_px']*bit_to_byte/1e6
        self.buffer_size_frames = round(BUFFER_SIZE_MB / frame_size_mb)
        # realloc buffers appears to be allocating ram on the pc side, not camera side.
        self.grabber.realloc_buffers(self.buffer_size_frames)  # allocate RAM buffer N frames
        self.log.info(f"buffer set to: {self.buffer_size_frames} frames")

    def start(self, frame_count=GENTL_INFINITE):
        """Start camera. If no frame count given, assume infinite frames"""
        self.grabber.start(frame_count=frame_count)

    def stop(self):
        self.grabber.stop()

    def grab_frame(self):
        """Retrieve a frame as a 2D numpy array with shape (rows, cols)."""
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
            # decimate binning
            return image[::self._binning, ::self._binning]
            # TODO ADD GPUTOOLS LINE HERE
        else:
            return image

    def signal_acquisition_state(self):
        """return a dict with the state of the acquisition buffers"""
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
        """Log camera metadata with the schema tag."""
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

    def _get_min_max_step_values(self):

        # gather min max values. all may not be available for certain cameras.
        # minimum exposure time
        # convert from us to ms
        try:
            self.min_exposure_time_ms = self.grabber.remote.get("ExposureTime.Min")/1e3
            self.log.info(f"min exposure time is: {self.min_exposure_time_ms} ms")
            print(f"min exposure time is: {self.min_exposure_time_ms} ms")
        except:
            self.log.debug(f"min exposure time not available for camera {self.id}")
        # maximum exposure time
        # convert from us to ms
        try:
            self.max_exposure_time_ms = self.grabber.remote.get("ExposureTime.Max")/1e3
            self.log.info(f"max exposure time is: {self.max_exposure_time_ms} ms")
            print(f"max exposure time is: {self.max_exposure_time_ms} ms")
        except:
            self.log.debug(f"max exposure time not available for camera {self.id}")
        # minimum width
        try:
            self.min_width_px = self.grabber.remote.get("Width.Min")
            self.log.info(f"min width is: {self.min_width_px} px")
            print(f"min width is: {self.min_width_px} px")
        except:
            self.log.debug(f"min width not available for camera {self.id}")
        # maximum width
        try:
            self.max_width_px = self.grabber.remote.get("Width.Max")
            self.log.info(f"max width is: {self.max_width_px} px")
            print(f"max width is: {self.max_width_px} px")
        except:
            self.log.debug(f"max width not available for camera {self.id}")
        # minimum height
        try:
            self.min_height_px = self.grabber.remote.get("Height.Min")
            self.log.info(f"min height is: {self.min_height_px} px")
            print(f"min height is: {self.min_height_px} px")
        except:
            self.log.debug(f"min height not available for camera {self.id}")
        # maximum height
        try:
            self.max_height_px = self.grabber.remote.get("Height.Max")
            self.log.info(f"max height is: {self.max_height_px} px")
            print(f"max height is: {self.max_height_px} px")
        except:
            self.log.debug(f"max height not available for camera {self.id}")
        # minimum offset x
        try:
            self.min_offset_x_px = self.grabber.remote.get("OffsetX.Min")
            self.log.info(f"min offset x is: {self.min_offset_x_px} px")
            print(f"min offset x is: {self.min_offset_x_px} px")
        except:
            self.log.debug(f"min offset x not available for camera {self.id}")
        # maximum offset x
        try:
            self.max_offset_x_px = self.grabber.remote.get("OffsetX.Max")
            self.log.info(f"max offset x is: {self.max_offset_x_px} px")
            print(f"max offset x is: {self.max_offset_x_px} px")
        except:
            self.log.debug(f"max offset x not available for camera {self.id}")
        # minimum offset y
        try:
            self.min_offset_y_px = self.grabber.remote.get("OffsetY.Min")
            self.log.info(f"min offset y is: {self.min_offset_y_px} px")
            print(f"min offset y is: {self.min_offset_y_px} px")
        except:
            self.log.debug(f"min offset y not available for camera {self.id}")
        # maximum offset y
        try:
            self.max_offset_y_px = self.grabber.remote.get("OffsetY.Max")
            self.log.info(f"max offset y is: {self.max_offset_y_px} px")
            print(f"max offset y is: {self.max_offset_y_px} px")
        except:
            self.log.debug(f"max offset y not available for camera {self.id}")
        # step exposure time
        # convert from us to ms
        try:
            self.step_exposure_time_ms = self.grabber.remote.get("ExposureTime.Inc")/1e3
            self.log.info(f"step exposure time is: {self.step_exposure_time_ms} ms")
            print(f"step exposure time is: {self.step_exposure_time_ms} ms")
        except:
            self.log.debug(f"step exposure time not available for camera {self.id}")
        # step width
        try:
            self.step_width_px = self.grabber.remote.get("Width.Inc")
            self.log.info(f"step width is: {self.step_width_px} px")
            print(f"step width is: {self.step_width_px} px")
        except:
            self.log.debug(f"step width not available for camera {self.id}")
        # step height
        try:
            self.step_height_px = self.grabber.remote.get("Height.Inc")
            self.log.info(f"step height is: {self.step_height_px} px")
            print(f"step height is: {self.step_height_px} px")
        except:
            self.log.debug(f"step height not available for camera {self.id}")
        # step offset x
        try:
            self.step_offset_x_px = self.grabber.remote.get("OffsetX.Inc")
            self.log.info(f"step offset x is: {self.step_offset_x_px} px")
            print(f"step offset x is: {self.step_offset_x_px} px")
        except:
            self.log.debug(f"step offset x not available for camera {self.id}")
        # step offset y
        try:
            self.step_offset_y_px = self.grabber.remote.get("OffsetY.Inc")
            self.log.info(f"step offset y is: {self.step_offset_y_px} px")
            print(f"step offset y is: {self.step_offset_y_px} px")
        except:
            self.log.debug(f"step offset y not available for camera {self.id}")

    def _query_binning(self):
        # egrabber defines 1 as 'X1', 2 as 'X2', 3 as 'X3'...
        # check only horizontal since we will use same binning for vertical
        binning_options = self.grabber.remote.get("@ee BinningHorizontal", dtype=list)
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
                    self.log.debug(f"{binning} will be implemented through software")
                    key = int(binning.replace("X", ""))
                    BINNING[key] = key

        print(BINNING)

        # initialize binning as 1
        self.grabber.remote.set("BinningHorizontal", BINNING[1])

    def _query_pixel_types(self):
        # egrabber defines as 'Mono8', 'Mono12', 'Mono16'...
        pixel_type_options = self.grabber.remote.get("@ee PixelFormat", dtype=list)
        for pixel_type in pixel_type_options:
            try:
                self.grabber.remote.set("PixelFormat", pixel_type)
                # generate lowercase string key
                key = pixel_type.lower()
                PIXEL_TYPES[key] = pixel_type
            except:
                self.log.debug(f"{pixel_type} not avaiable on this camera")
        # initialize pixel type as mono16
        self.grabber.remote.set("PixelFormat", PIXEL_TYPES["mono16"])

        # once the pixel types are found, detrmine line intervals
        self._query_line_intervals()

    def _query_line_intervals(self):

        for key in PIXEL_TYPES:
            # set pixel type
            self.grabber.remote.set("PixelFormat", PIXEL_TYPES[key])
            # check max acquisition rate, used to determine line interval
            max_frame_rate = self.grabber.remote.get("AcquisitionFrameRate.Max")
            line_interval_s = (1/max_frame_rate)/self.sensor_height_px
            # conver from s to us and store
            LINE_INTERVALS_US[key] = line_interval_s*1e6