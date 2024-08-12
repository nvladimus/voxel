from typing import Tuple, Dict, List, Optional, Union, Literal, Any

import numpy as np

from voxel.descriptors.deliminated_property import deliminated_property
from voxel.devices.camera import VoxelCamera
from voxel.devices.camera.typings import (
    BYTES_PER_MB,
    Binning, BinningLUT,
    PixelType, PixelTypeLUT, PixelTypeInfo,
    BitPackingMode, BitPackingModeLUT,
    TriggerSettingsLUT, TriggerMode, TriggerSource, TriggerPolarity, TriggerSettings,
    VoxelFrame, AcquisitionState
)
from voxel.devices.camera.vieworks.egrabber import (
    EGenTL, EGrabber, EGrabberDiscovery, Buffer, ct,
    GENTL_INFINITE, BUFFER_INFO_BASE, INFO_DATATYPE_PTR, INFO_DATATYPE_SIZET, STREAM_INFO_NUM_DELIVERED,
    STREAM_INFO_NUM_QUEUED, STREAM_INFO_NUM_AWAIT_DELIVERY, STREAM_INFO_NUM_UNDERRUN, query,
)
from voxel.devices.device import DeviceConnectionError
from voxel.devices.utils.geometry import Vec2D
from voxel.devices.utils.singleton import Singleton


class EGenTLSingleton(EGenTL, metaclass=Singleton):
    """Singleton wrapper around the EGrabber SDK."""

    def __init__(self):
        super().__init__()


class VieworksCamera(VoxelCamera):
    """VoxelCamera implementation for Vieworks cameras using the EGrabber SDK.
    :param id: Voxel ID for the device.
    :param serial_number: Serial number of the camera - used to discover the camera.
    :type id: str
    :type serial_number: str
    """
    BUFFER_SIZE_MB = 2400

    gentl = EGenTLSingleton()

    def __init__(self, id, serial_number):
        super().__init__(id)
        self.serial_number = serial_number

        self.grabber, self.egrabber = self._discover_camera(self.gentl, self.serial_number)

        # Flags
        self._buffer_allocated = False

        # LUTs and cached properties
        self._binning_cache: Optional[Binning] = None
        self._binning_lut: BinningLUT = self._query_binning_lut()
        self._pixel_type_cache: Optional[PixelType] = None
        self._pixel_type_lut: PixelTypeLUT = self._query_pixel_type_lut()
        self._bit_packing_mode_cache: Optional[BitPackingMode] = None
        self._bit_packing_mode_lut: BitPackingModeLUT = self._query_bit_packing_mode_lut()
        self._trigger_setting_cache: Optional[TriggerSettings] = None
        self._trigger_settings_lut: TriggerSettingsLUT = self._query_trigger_settings_lut()

        # delimination properties
        self._delimination_props = {
            "Width": {"Min": None, "Max": None, "Inc": None},
            "Height": {"Min": None, "Max": None, "Inc": None},
            "ExposureTime": {"Min": None, "Max": None, "Inc": None}
        }

    @deliminated_property(
        minimum=lambda self: self._query_delimination_prop("Height", "Min"),
        maximum=lambda self: self._query_delimination_prop("Height", "Max"),
        step=lambda self: self._query_delimination_prop("Height", "Inc"),
        unit='px'
    )
    def roi_width_px(self) -> int:
        """Get the width of the ROI in pixels.
        :return: The width in pixels.
        :rtype: int
        """
        try:
            return int(self.grabber.remote.get("Width"))
        except Exception as e:
            self.log.error(f"Failed to get ROI width: {e}")
            return 0

    @roi_width_px.setter
    def roi_width_px(self, value: int) -> None:
        """Set the width of the ROI in pixels.
        :param value: The width in pixels.
        :type value: int
        """
        self.grabber.remote.set("OffsetX", 0)
        step_size = self._query_delimination_prop("Width", "Inc")
        centered_offset = round(((self.sensor_width_px - value) / 2) / step_size) * step_size
        self.grabber.remote.set("OffsetX", centered_offset)
        self.grabber.remote.set("Width", value)
        self.log.info(f"Set ROI width to {value} px")
        self._invalidate_delimination_prop("Width")

    @property
    def roi_width_offset_px(self) -> int:
        """Get the offset of the ROI width in pixels.
        :return: The offset in pixels.
        :rtype: int
        """
        try:
            return int(self.grabber.remote.get("OffsetX"))
        except Exception as e:
            self.log.error(f"Failed to get ROI width offset: {e}")
            return 0

    @property
    def sensor_width_px(self) -> int:
        """Get the sensor width in pixels.
        :return: The sensor width in pixels.
        :rtype: int
        """
        try:
            return int(self.grabber.remote.get("SensorWidth"))
        except Exception as e:
            self.log.error(f"Failed to get sensor width: {e}")
            return 0

    @deliminated_property(
        minimum=lambda self: self._query_delimination_prop("Height", "Min"),
        maximum=lambda self: self._query_delimination_prop("Height", "Max"),
        step=lambda self: self._query_delimination_prop("Height", "Inc"),
        unit='px'
    )
    def roi_height_px(self) -> int:
        """Get the height of the ROI in pixels.
        :return: The height in pixels.
        :rtype: int
        """
        try:
            return int(self.grabber.remote.get("Height"))
        except Exception as e:
            self.log.error(f"Failed to get ROI height: {e}")
            return 0

    @roi_height_px.setter
    def roi_height_px(self, value: int) -> None:
        """Set the height of the ROI in pixels.
        :param value: The height in pixels.
        :type value: int
        """
        self.grabber.remote.set("OffsetY", 0)
        step_size = self._query_delimination_prop("Height", "Inc")
        centered_offset = round(((self.sensor_height_px - value) / 2) / step_size) * step_size
        self.grabber.remote.set("OffsetY", centered_offset)
        self.grabber.remote.set("Height", value)
        self.log.info(f"Set ROI height to {value} px")
        self._invalidate_delimination_prop("Height")

    @property
    def roi_height_offset_px(self) -> int:
        """Get the offset of the ROI height in pixels.
        :return: The offset in pixels.
        :rtype: int
        """
        try:
            return int(self.grabber.remote.get("OffsetY"))
        except Exception as e:
            self.log.error(f"Failed to get ROI height offset: {e}")
            return 0

    @property
    def sensor_height_px(self) -> int:
        """Get the sensor height in pixels.
        :return: The sensor height in pixels.
        :rtype: int
        """
        try:
            return int(self.grabber.remote.get("SensorHeight"))
        except Exception as e:
            self.log.error(f"Failed to get sensor height: {e}")
            return 0

    @property
    def binning(self) -> Binning:
        """Get the binning setting.
        :return: The binning setting i.e Literal[1, 2, 4]
        :rtype: Binning
        """
        if self._binning_cache is None:
            grabber_binning = self.grabber.remote.get("BinningHorizontal")
            try:
                self._binning_cache = next(k for k, v in self._binning_lut.items() if v == grabber_binning)
            except KeyError:
                self.log.error(f"Grabber binning ({grabber_binning}) not found in LUT({self._binning_lut})")
                self._binning_cache = Binning(1)  # default to 1x1
        return self._binning_cache

    @binning.setter
    def binning(self, binning: Binning) -> None:
        """Set the binning setting.
        :param binning: The binning setting i.e Literal[1, 2, 4]
        :type binning: Binning
        """
        if binning not in self._binning_lut:
            self.log.error(f"Invalid binning value: {binning}")
            return
        self.grabber.remote.set("BinningHorizontal", self._binning_lut[binning])
        self.grabber.remote.set("BinningVertical", self._binning_lut[binning])
        self.log.info(f"Set binning to {binning}")
        self._binning_cache = None
        # TODO: Check if binning affects exposure time delimination props
        self._invalidate_all_delimination_props()

    @property
    def image_size_px(self) -> Vec2D:
        """Get the image size in pixels.
        :return: The image size in pixels.
        :rtype: Vec2D
        """
        return Vec2D(self.roi_width_px, self.roi_height_px) // self.binning

    @property
    def pixel_type(self) -> PixelType:
        """Get the pixel type of the camera.
        :return: The pixel type.
        :rtype: PixelType
        """
        if not self._pixel_type_cache:
            grabber_pixel_type = self.grabber.remote.get("PixelFormat")
            try:
                self._pixel_type_cache = next(
                    k for k, v in self._pixel_type_lut.items() if v.repr == grabber_pixel_type)
            except KeyError:
                self.log.error(f"Grabber pixel type ({grabber_pixel_type}) not found in LUT({self._pixel_type_lut})")
                self._pixel_type_cache = PixelType.MONO8
        return self._pixel_type_cache

    @pixel_type.setter
    def pixel_type(self, pixel_type: PixelType) -> None:
        """Set the pixel type of the camera.
        :param pixel_type: The pixel type (enum)
        :type pixel_type: PixelType
        """
        if pixel_type not in self._pixel_type_lut:
            self.log.error(f"Invalid pixel type: {pixel_type}")
            return
        self.grabber.remote.set("PixelFormat", self._pixel_type_lut[pixel_type].repr)
        self._pixel_type_cache = None
        self.log.info(f"Set pixel type to {pixel_type}")

    @property
    def bit_packing_mode(self) -> BitPackingMode:
        """Get the bit packing mode of the camera.
        :return: The bit packing mode.
        :rtype: BitPackingMode
        """
        if not self._bit_packing_mode_cache:
            grabber_bit_packing = self.grabber.remote.get("UnpackingMode")
            try:
                self._bit_packing_mode_cache = next(
                    k for k, v in self._bit_packing_mode_lut.items() if v == grabber_bit_packing)
            except KeyError:
                self.log.error(
                    f"Grabber bit packing mode ({grabber_bit_packing}) not found in LUT({self._bit_packing_mode_lut})")
                self._bit_packing_mode_cache = BitPackingMode.NONE
        return self._bit_packing_mode_cache

    @bit_packing_mode.setter
    def bit_packing_mode(self, bit_packing_mode: BitPackingMode) -> None:
        """Set the bit packing mode of the camera.
        :param bit_packing_mode: The bit packing mode (enum)
        :type bit_packing_mode: BitPackingMode
        """
        if bit_packing_mode not in self._bit_packing_mode_lut:
            self.log.error(f"Invalid bit packing mode: {bit_packing_mode}")
            return
        self.grabber.remote.set("UnpackingMode", self._bit_packing_mode_lut[bit_packing_mode])
        self._bit_packing_mode_cache = None
        self.log.info(f"Set bit packing mode to {bit_packing_mode}")

    @deliminated_property(
        minimum=lambda self: self._query_delimination_prop("ExposureTime", "Min") / 1000,
        maximum=lambda self: self._query_delimination_prop("ExposureTime", "Max") / 1000,
        step=lambda self: self._query_delimination_prop("ExposureTime", "Inc") / 1000,
    )
    def exposure_time_ms(self) -> int:
        """Get the exposure time in microseconds.
        :return: The exposure time in microseconds.
        :rtype: int
        """
        try:
            return int(self.grabber.remote.get("ExposureTime"))
        except Exception as e:
            self.log.error(f"Failed to get exposure time: {e}")
            return 0

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: int) -> None:
        """Set the exposure time in milliseconds.
        :param exposure_time_ms: The exposure time in milliseconds.
        :type exposure_time_ms: int
        """
        self.grabber.remote.set("ExposureTime", exposure_time_ms)
        self.log.info(f"Set exposure time to {exposure_time_ms} ms")
        self._invalidate_delimination_prop("ExposureTime")

    @property
    def line_interval_us(self) -> float:
        """Get the line interval in microseconds. \n
        Note: The line interval is the time between adjacent rows of pixels activating on the sensor.
        :return: The line interval in microseconds.
        :rtype: float
        """
        return self._pixel_type_lut[self.pixel_type].line_interval_us

    @property
    def frame_time_ms(self) -> float:
        """Get the frame time in milliseconds.
        :return: The frame time in milliseconds.
        :rtype: float
        """
        return (self.line_interval_us * self.roi_height_px / 1000) + self.exposure_time_ms

    @property
    def trigger(self) -> TriggerSettings:
        """
        Get the trigger settings of the camera.
        :return: The trigger settings.
        :rtype: TriggerSettings
        """
        if not self._trigger_setting_cache:
            try:
                mode = TriggerMode[self.grabber.remote.get("TriggerMode").upper()]
                source = TriggerSource[self.grabber.remote.get("TriggerSource").upper()]
                polarity = TriggerPolarity[self.grabber.remote.get("TriggerActivation").upper().replace("EDGE", "")]
                self._trigger_setting_cache = TriggerSettings(mode, source, polarity)
            except Exception as e:
                self.log.error(f"Error getting trigger settings: {str(e)}")
                # Return a default or raise an exception based on your error handling strategy
                raise ValueError("Failed to get trigger settings")
        return self._trigger_setting_cache

    @trigger.setter
    def trigger(self, settings: TriggerSettings) -> None:
        """
        Set the trigger settings of the camera.
        :param settings: The trigger settings to set.
        :type settings: TriggerSettings
        """
        try:
            self.grabber.remote.set("TriggerMode", self._trigger_settings_lut.mode[settings.mode])
            self.grabber.remote.set("TriggerSource", self._trigger_settings_lut.source[settings.source])
            self.grabber.remote.set("TriggerActivation", self._trigger_settings_lut.polarity[settings.polarity])
            self._trigger_setting_cache = settings
        except Exception as e:
            self.log.error(f"Error setting trigger settings: {str(e)}")
            raise ValueError("Failed to set trigger settings")

    def prepare(self) -> None:
        """
        Prepare the camera to acquire images.

        This method sets up the camera buffer for Vieworks cameras.
        It calculates the appropriate buffer size based on the current camera settings
        and allocates the buffer in PC RAM.
        :raises RuntimeError: If the camera preparation fails.
        """
        self.log.info("Preparing camera for acquisition")

        def get_bits_per_pixel(pixel_type: PixelType) -> int:
            if pixel_type in (PixelType.RGB8, PixelType.RGB10, PixelType.RGB12, PixelType.RGB14):
                return int(pixel_type.name[3:]) * 3  # 3 channels
            try:
                return int(pixel_type.name[-2:])
            except ValueError:
                raise ValueError(f"Unable to determine bit depth from pixel type: {pixel_type}")

        try:
            bits_per_pixel = get_bits_per_pixel(self.pixel_type)
            bytes_per_pixel = (bits_per_pixel + 7) // 8  # Round up to nearest byte

            frame_size_bytes = self.roi_width_px * self.roi_height_px * bytes_per_pixel
            frame_size_mb = frame_size_bytes / BYTES_PER_MB

            buffer_size_frames = max(1, round(self.BUFFER_SIZE_MB / frame_size_mb))

            self.log.info(f"Calculated frame size: {frame_size_mb:.2f} MB")
            self.log.info(f"Allocating buffer for {buffer_size_frames} frames")

            # Allocate RAM buffer for N frames
            self.grabber.realloc_buffers(buffer_size_frames)

            self.log.info(f"Prepared camera with {buffer_size_frames} buffers")

            self._buffer_allocated = True

        except Exception as e:
            self.log.error(f"Error preparing camera: {str(e)}")
            raise RuntimeError("Failed to prepare camera") from e

    def start(self, frame_count: int = GENTL_INFINITE):
        """
        Start the camera to acquire a certain number of frames. \n
        If frame number is not specified, acquires infinitely until stopped. \n
        Initializes the camera buffer.

        :param frame_count: The number of frames to acquire. Default is infinite.
        :type frame_count: int
        """
        if not self._buffer_allocated:
            self.prepare()
        self.grabber.start(frame_count)

    def stop(self):
        """Stop the camera from acquiring frames."""
        self.grabber.stop()
        self._buffer_allocated = False

    def close(self):
        """Close the camera and release all resources."""
        del self.grabber
        del self.egrabber
        self._buffer_allocated = False

    def reset(self):
        """Reset the camera to default settings."""
        del self.grabber
        self.grabber = EGrabber(
            self.gentl,
            self.egrabber["interface"],
            self.egrabber["device"],
            self.egrabber["stream"],
            remote_required=True
        )
        self._invalidate_all_delimination_props()
        self._regenerate_all_luts()
        self._buffer_allocated = False

    def grab_frame(self) -> VoxelFrame:
        """
        Grab a frame from the camera buffer. \n
        If binning is via software, the GPU binned \n
        image is computed and returned.

        :return: The camera frame of size (height, width).
        :rtype: VoxelFrame
        Note:
            VoxelFrame is a numpy array of uint_ type.
        """
        # Note: creating the buffer and then "pushing" it at the end has the
        #   effect of moving the internal camera frame buffer from the output
        #   pool back to the input pool, so it can be reused.
        column_count = self.grabber.remote.get("Width")
        row_count = self.grabber.remote.get("Height")
        timeout_ms = 1000
        with (Buffer(self.grabber, timeout=timeout_ms) as buffer):
            ptr = buffer.get_info(BUFFER_INFO_BASE, INFO_DATATYPE_PTR)  # pointer to new frame
            data = ct.cast(ptr, ct.POINTER(ct.c_ubyte * column_count * row_count * 2)).contents
            frame = np.frombuffer(
                data, count=int(column_count * row_count), dtype=np.uint16
            ).reshape((row_count, column_count))
            return frame

    @property
    def acquisition_state(self) -> AcquisitionState:
        """
        Get the current acquisition state of the camera.
        :return: The acquisition state.
        :rtype: AcquisitionState
        Notes:
            AcquisitionState is a dataclass with the following fields:
                - frame_index: The current frame index.
                - input_buffer_size: The size of the input buffer.
                - output_buffer_size: The size of the output buffer.
                - dropped_frames: The number of dropped frames.
                - frame_rate_fps: The current frame rate.
                - data_rate_mbs: The current data rate.
        Detailed description of constants here:
        https://documentation.euresys.com/Products/Coaxlink/Coaxlink/en-us/Content/IOdoc/egrabber-reference/namespace_gen_t_l.html#a6b498d9a4c08dea2c44566722699706e
        """

        def get_acquisition_stream_info(info_cmd: int | str, default: Any = None, is_metric: bool = False) -> int:
            try:
                if is_metric:
                    return self.grabber.stream.get(info_cmd)
                else:
                    return self.grabber.stream.get_info(info_cmd, INFO_DATATYPE_SIZET)
            except Exception as e:
                self.log.error(f"Acquisition state: Failed to get {info_cmd}: {e}")
                return default

        return AcquisitionState(
            frame_index=get_acquisition_stream_info(STREAM_INFO_NUM_DELIVERED),
            input_buffer_size=get_acquisition_stream_info(STREAM_INFO_NUM_QUEUED),
            output_buffer_size=get_acquisition_stream_info(STREAM_INFO_NUM_AWAIT_DELIVERY),
            dropped_frames=get_acquisition_stream_info(STREAM_INFO_NUM_UNDERRUN),
            data_rate_mbs=get_acquisition_stream_info("StatisticsDataRate", is_metric=True),
            frame_rate_fps=get_acquisition_stream_info("StatisticsFrameRate", is_metric=True)
        )

    def log_metadata(self):
        """
        Log all metadata from the camera to the logger.
        """

        def log_component_metadata(comp_name, comp):
            if comp is None:
                return

            categories = comp.get(query.categories())
            for category in categories:
                features = comp.get(query.features_of(category))
                for feature in features:
                    if (comp.get(query.available(feature)) and
                            comp.get(query.readable(feature)) and
                            not comp.get(query.command(feature))):

                        if comp_name == "remote" and feature in ["BalanceRatioSelector", "BalanceWhiteAuto"]:
                            continue

                        value = comp.get(feature)
                        self.log.info(f"{comp_name}, {feature}, {value}")

        components = [
            ("device", self.grabber.device),
            ("remote", self.grabber.remote),
            ("stream", self.grabber.stream),
            ("interface", self.grabber.interface),
            ("system", self.grabber.system)
        ]

        for component_name, component in components:
            self.log.info(f"Logging {component_name} parameters")
            log_component_metadata(component_name, component)

    # Private methods #########################################################

    def _regenerate_all_luts(self) -> None:
        self._binning_lut = self._query_binning_lut()
        self._pixel_type_lut = self._query_pixel_type_lut()
        self._bit_packing_mode_lut = self._query_bit_packing_mode_lut()
        self._trigger_settings_lut = self._query_trigger_settings_lut()

    def _query_binning_lut(self) -> BinningLUT:
        """
        Internal function that queries camera SDK to determine binning options.
        Note:
            EGrabber defines binning settings as strings: 'X1', 'X2' etc.
            For all use-cases, we assume that both the horizontal and vertical
            binning are the same. Therefore, we only consider the horizontal
        """
        lut = BinningLUT()
        init_binning = None
        try:
            init_binning = self.grabber.remote.get("BinningHorizontal")
            binning_options = self.grabber.remote.get("@ee BinningHorizontal", dtype=list)
            for binning in binning_options:
                try:
                    self.grabber.remote.set("BinningHorizontal", binning)
                    binning_int = int(binning[1:])
                    lut[Binning(binning_int)] = binning
                except (ValueError, KeyError) as e:
                    self.log.warning(f"Failed to process binning option {binning}: {str(e)}")
        except Exception as e:
            self.log.error(f"Error querying binning options: {str(e)}")
        finally:
            if init_binning:
                try:
                    self.grabber.remote.set("BinningHorizontal", init_binning)
                except Exception as e:
                    self.log.error(f"Failed to restore initial binning setting: {str(e)}")
        return lut

    def _query_pixel_type_lut(self) -> PixelTypeLUT:
        """
        Internal function that queries camera SDK to determine pixel type options.
        Note:
            EGrabber defines pixel type settings as strings: 'Mono8', 'Mono12' 'Mono16' etc.
            We convert these to PixelType enums for easier handling.
        """

        def query_line_interval(pixel_type_repr: str) -> Optional[float]:
            try:
                self.grabber.remote.set("PixelFormat", pixel_type_repr)
                return self.grabber.remote.get("LineInterval")
            except Exception as er:
                self.log.error(f"Failed to get line interval for pixel type {pixel_type_repr}: {er}")
                return None

        lut = PixelTypeLUT()
        init_pixel_type = None
        try:
            pixel_type_options = self.grabber.remote.get("@ee PixelFormat", dtype=list)
            init_pixel_type = self.grabber.remote.get("PixelFormat")
            for pixel_type in pixel_type_options:
                try:
                    line_interval = query_line_interval(pixel_type)
                    if line_interval is None:
                        continue
                    info = PixelTypeInfo(repr=pixel_type, line_interval_us=line_interval)
                    lut_key = pixel_type.upper().replace(" ", "")  # convert 'Mono 8' to 'MONO8'
                    lut[PixelType[lut_key]] = info
                except KeyError as e:
                    self.log.warning(f"Failed to convert pixel type option {pixel_type} to PixelType: {str(e)}")
                except Exception as e:
                    self.log.warning(f"Unexpected error processing pixel type {pixel_type}: {str(e)}")
        except Exception as e:
            self.log.error(f"Error querying pixel type options: {str(e)}")
        finally:
            if init_pixel_type:
                try:
                    self.grabber.remote.set("PixelFormat", init_pixel_type)
                except Exception as e:
                    self.log.error(f"Failed to restore initial pixel type setting: {str(e)}")
        return lut

    def _query_bit_packing_mode_lut(self) -> BitPackingModeLUT:
        """
        Internal function that queries camera SDK to determine the bit packing mode options.
        Note:
            EGrabber defines the bit packing settings as strings: 'LSB', 'MSB', 'None', etc.
            We convert these to BitPackingMode enums for easier handling.
        """
        lut = BitPackingModeLUT()
        init_bit_packing = None
        try:
            bit_packing_options = self.grabber.remote.get("@ee UnpackingMode", dtype=list)
            init_bit_packing = self.grabber.remote.get("UnpackingMode")
            for bit_packing in bit_packing_options:
                try:
                    self.grabber.remote.set("UnpackingMode", bit_packing)
                    lut_key = BitPackingMode[bit_packing.upper()]
                    lut[lut_key] = bit_packing
                except KeyError as e:
                    self.log.warning(f"Failed to convert bit packing option {bit_packing} to BitPackingMode: {str(e)}")
                except Exception as e:
                    self.log.warning(f"Unexpected error processing bit packing option {bit_packing}: {str(e)}")
        except Exception as e:
            self.log.error(f"Error querying bit packing mode options: {str(e)}")
        finally:
            if init_bit_packing:
                try:
                    self.grabber.remote.set("UnpackingMode", init_bit_packing)
                except Exception as e:
                    self.log.error(f"Failed to restore initial bit packing mode setting: {str(e)}")
        return lut

    def _query_trigger_settings_lut(self) -> TriggerSettingsLUT:
        """
        Internal function that queries camera SDK to determine the trigger settings options.
        Note:
            EGrabber defines trigger configuration as:
                - TriggerMode: 'On', 'Off'
                - TriggerSource: 'Internal', 'External'
                - TriggerActivation: 'Rising', 'Falling'
        """

        def query_trigger_setting_options(
                setting_name: Literal['TriggerMode', 'TriggerSource', 'TriggerActivation']
        ) -> Dict[Union[TriggerMode, TriggerSource, TriggerPolarity], str]:
            def is_valid_setting(test_setting: str) -> bool:
                try:
                    current_setting = self.grabber.remote.get(setting_name)
                    if test_setting != current_setting:
                        self.grabber.remote.set(setting_name, test_setting)
                    return True
                except Exception as er:
                    self.log.warning(f"Failed to set {setting_name} to {test_setting}: {str(er)}")
                    return False

            setting_dict = {}
            init_setting = None
            try:
                init_setting = self.grabber.remote.get(setting_name)
                setting_options = self.grabber.remote.get(f'@ee {setting_name}', dtype=list)
                for setting in setting_options:
                    if is_valid_setting(setting):
                        setting_dict_key = setting.upper().replace(" ", "")
                        enum_type = {
                            'TriggerMode': TriggerMode,
                            'TriggerSource': TriggerSource,
                            'TriggerActivation': TriggerPolarity
                        }[setting_name]
                        setting_dict[enum_type[setting_dict_key]] = setting
            except Exception as e:
                self.log.error(f"Error querying {setting_name} options: {str(e)}")
            finally:
                if init_setting is not None:
                    try:
                        self.grabber.remote.set(setting_name, init_setting)
                    except Exception as e:
                        self.log.error(f"Failed to restore initial {setting_name} setting: {str(e)}")
            return setting_dict

        return TriggerSettingsLUT(
            mode=query_trigger_setting_options('TriggerMode'),
            source=query_trigger_setting_options('TriggerSource'),
            polarity=query_trigger_setting_options('TriggerActivation')
        )

    def _query_delimination_prop(self, prop_name: str, limit_type: str) -> int | float:
        if self._delimination_props[prop_name][limit_type] is None:
            value = self.grabber.remote.get(f'{prop_name}.{limit_type.capitalize()}')
            self._delimination_props[prop_name][limit_type] = value
        return self._delimination_props[prop_name][limit_type]

    def _query_all_delimination_props(self):
        for prop_name in self._delimination_props:
            for limit_type in self._delimination_props[prop_name]:
                self._query_delimination_prop(prop_name, limit_type)

    def _invalidate_delimination_prop(self, prop_name: str):
        if prop_name in self._delimination_props:
            self._delimination_props[prop_name] = {
                "Min": None,
                "Max": None,
                "Step": None,
            }

    def _invalidate_all_delimination_props(self):
        for prop_name in self._delimination_props:
            self._invalidate_delimination_prop(prop_name)

    @staticmethod
    def _discover_camera(gentl_instance: EGenTLSingleton, serial_number: str) -> Tuple[EGrabber, Dict[str, int]]:
        def discover_cameras() -> Dict[str, List[Dict[str, int]]]:
            discovery = EGrabberDiscovery(gentl_instance)
            discovery.discover()
            _egrabber_list = {"grabbers": []}
            for interface_index in range(discovery.interface_count()):
                for device_index in range(discovery.device_count(interface_index)):
                    if discovery.device_info(interface_index, device_index).deviceVendorName:
                        for stream_index in range(
                                discovery.stream_count(interface_index, device_index)
                        ):
                            _egrabber_list["grabbers"].append(
                                {
                                    "interface": interface_index,
                                    "device": device_index,
                                    "stream": stream_index,
                                }
                            )
            return _egrabber_list

        egrabber_list = discover_cameras()

        if not egrabber_list["grabbers"]:
            raise DeviceConnectionError(
                "No valid cameras found. Check connections and close any software."
            )

        for egrabber in egrabber_list["grabbers"]:
            grabber = EGrabber(
                gentl_instance,
                egrabber["interface"],
                egrabber["device"],
                egrabber["stream"],
                remote_required=True,
            )
            grabber_serial: Optional[str] = grabber.remote.get("DeviceSerialNumber") if grabber.remote else None
            if grabber_serial == serial_number:
                return grabber, egrabber

        raise DeviceConnectionError(f"No grabber found for S/N: {serial_number}")
