import logging
import numpy
from egrabber import *

# constants for VP-151MX camera

class Camera:

    def __init__(self, camera_id):
        """Connect to hardware.
        
        :param camera_cfg: cfg for camera.
        """
        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @property
    def exposure_time_ms(self):
        pass

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float):
        pass

    @property
    def roi(self):
        return {'width_px': self.grabber.remote.get("Width"),
                'height_px': self.grabber.remote.get("Height"),
                'width_offset_px': self.grabber.remote.get("OffsetX"),
                'height_offest_px': self.grabber.remote.get("OffsetY")}

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

        self.grabber.remote.set("OffsetX", 0)
        self.grabber.remote.set("Width", width_px)
        # width offset must be a multiple of the divisible width in px
        centered_width_offset_px = round((sensor_width_px/2 - width_px/2)/DIVISIBLE_WIDTH_PX)*DIVISIBLE_WIDTH_PX  
        self.grabber.remote.set("OffsetX", centered_width_offset_px)    
        self.grabber.remote.set("OffsetY", 0)
        self.grabber.remote.set("Height", height_px)
        height_px = self.grabber.remote.get("Height")
        # Height offset must be a multiple of the divisible height in px
        centered_height_offset_px = round((sensor_height_px/2 - height_px/2)/DIVISIBLE_HEIGHT_PX)*DIVISIBLE_HEIGHT_PX  
        self.grabber.remote.set("OffsetY", centered_height_offset_px)
        self.log.info(f"roi set to: {width_px} x {height_px} [width x height]")
        self.log.info(f"roi offset set to: {centered_width_offset_px} x {centered_height_offset_px} [width x height]")

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
        self.log.info(f"pixel type set_to: {pixel_type_bits}")

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

    @property
    def line_interval_us(self):
        pixel_type = self.pixel_type
        return LINE_INTERVALS_US[pixel_type]

    @line_interval_us.setter
    def line_interval_us(self):
        self.log.warning(f"line interval is controlled by pixel type for the VP-151MX camera!")
        pass

    @property
    def readout_mode(self):
        self.log.warning(f"readout mode cannot be set for the VP-151MX camera!")

    @readout_mode.setter
    def readout_mode(self):
        self.log.warning(f"readout mode cannot be set for the VP-151MX camera!")
        pass

    @property
    def readout_direction(self):
        self.log.warning(f"readout direction cannot be set for the VP-151MX camera!")

    @readout_direction.setter
    def readout_direction(self):
        self.log.warning(f"readout direction cannot be set for the VP-151MX camera!")
        pass

    @property
    def trigger(self):
        mode = self.grabber.remote.get("TriggerMode")
        source = self.grabber.remote.get("TriggerSource")
        polarity = self.grabber.remote.get("TriggerActivation")
        return {"mode": next(key for key, value in TRIGGER_MODES.items() if value == mode),
                "source": next(key for key, value in TRIGGER_SOURCES.items() if value == source),
                "polarity": next(key for key, value in TRIGGER_POLARITY.items() if value == polarity)}

    @trigger.setter
    def trigger(self, value: tuple):

        mode, source, polarity = value

        valid_mode = list(TRIGGER_MODES.keys())
        if mode not in valid_mode:
            raise ValueError("mode must be one of %r." % valid)
        valid_source = list(TRIGGER_SOURCES.keys())
        if source not in valid_source:
            raise ValueError("source must be one of %r." % valid)
        valid_polarity = list(TRIGGER_POLARITY.keys())
        if polarity not in valid_polarity:
            raise ValueError("polarity must be one of %r." % valid)

        # Note: Setting TriggerMode if it's already correct will throw an error
        if self.grabber.remote.get("TriggerMode") != mode:  # set camera to external trigger mode
            self.grabber.remote.set("TriggerMode", TRIGGER_MODES[mode])
        self.grabber.remote.set("TriggerSource", TRIGGER_SOURCES[source])
        self.grabber.remote.set("TriggerActivation", TRIGGER_POLARITY[polarity])
        self.log.info(f"trigger set to, mode: {mode}, source: {source}, polarity: {polarity}")

    @property
    def binning(self): 
        self.log.warning(f"binning is not available on the VP-151MX")
        pass

    @binning.setter
    def binning(self, binning: int): 
        self.log.warning(f"binning is not available on the VP-151MX")
        pass

    @property
    def sensor_width_px(self):
        return MAX_WIDTH_PX

    @property
    def sensor_height_px(self):
        return MAX_HEIGHT_PX

    @property
    def mainboard_temperature_c(self):
        """get the mainboard temperature in degrees C."""
        self.grabber.remote.set("DeviceTemperatureSelector", "Mainboard")
        return self.grabber.remote.get("DeviceTemperature")

    @property
    def sensor_temperature_c(self):
        """get the sensor temperature in degrees C."""
        self.grabber.remote.set("DeviceTemperatureSelector", "Sensor")
        return self.grabber.remote.get("DeviceTemperature")

    def prepare(self, buffer_size_frames: int = 8):
        # realloc buffers appears to be allocating ram on the pc side, not camera side.
        if buffer_size_frames < MIN_BUFFER_SIZE or \
           buffer_size_frames > MAX_BUFFER_SIZE:
            self.log.error(f"buffer size must be >{MIN_BUFFER_SIZE} frames \
                             and <{MAX_BUFFER_SIZE} frames")
            raise ValueError(f"buffer size must be >{MIN_BUFFER_SIZE} frames \
                             and <{MAX_BUFFER_SIZE} frames")
        self.grabber.realloc_buffers(buffer_size_frames)  # allocate RAM buffer N frames
        self.log.info(f"buffer set to: {buffer_size_frames} frames")

    def start(self, frame_count: int, live: bool = False):
        if live:
            self.grabber.start()
        else:
            self.grabber.start(frame_count)

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
            return image

    def get_camera_acquisition_state(self):
        """return a dict with the state of the acquisition buffers"""
        # Detailed description of constants here:
        # https://documentation.euresys.com/Products/Coaxlink/Coaxlink/en-us/Content/IOdoc/egrabber-reference/
        # namespace_gen_t_l.html#a6b498d9a4c08dea2c44566722699706e
        state = {}
        state['frame_index'] = self.grabber.stream.get_info(STREAM_INFO_NUM_DELIVERED, INFO_DATATYPE_SIZET)
        state['in_buffer_size'] = self.grabber.stream.get_info(STREAM_INFO_NUM_QUEUED,
                                                               INFO_DATATYPE_SIZET)
        state['out_buffer_size'] = self.grabber.stream.get_info(STREAM_INFO_NUM_AWAIT_DELIVERY,
                                                                INFO_DATATYPE_SIZET)
         # number of underrun, i.e. dropped frames
        state['dropped_frames'] = self.grabber.stream.get_info(STREAM_INFO_NUM_UNDERRUN,
                                                               INFO_DATATYPE_SIZET)
        state['data_rate'] = self.grabber.stream.get('StatisticsDataRate')
        state['frame_rate'] = self.grabber.stream.get('StatisticsFrameRate')
        self.log.debug(f"frame: {state['frame_index']}, "
                       f"input buffer size: {state['in_buffer_size']}, "
                       f"output buffer size: {state['out_buffer_size']}, "
                       f"dropped_frames: {state['dropped_frames']}, "
                       f"data rate: {state['data_rate']:.2f} [MB/s], "
                       f"frame rate: {state['frame_rate']:.2f} [fps].")
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