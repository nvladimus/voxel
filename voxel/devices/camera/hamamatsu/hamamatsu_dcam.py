import time
from enum import Enum
from typing import Optional, Literal, Dict, Union, Tuple, TypeAlias

import numpy as np
from numpy._typing import NDArray

from voxel.descriptors.deliminated_property import deliminated_property
from voxel.descriptors.enumerated_property import enumerated_property, set_ith_option
from voxel.devices.base import DeviceConnectionError, VoxelDevice
from voxel.devices.camera.base import VoxelCamera
from voxel.devices.camera.hamamatsu.dcam.dcam import (
    DCAM_IDSTR,
    DCAMCAP_TRANSFERINFO,
    DCAMERR,
    Dcam,
    Dcamapi,
    byref,
    dcamcap_transferinfo,
)
from voxel.devices.camera.hamamatsu.dcam.dcamapi4 import DCAMPROP_ATTR
from voxel.devices.camera.hamamatsu.typings import SensorModeLUT, SensorMode, ReadoutDirectionLUT, ReadoutDirection, \
    TriggerModeLUT, TriggerSourceLUT, TriggerPolarityLUT, TriggerMode, TriggerSource, TriggerPolarity, TriggerActiveLUT, \
    TriggerActive, TriggerSettings
from voxel.devices.camera.typings import (
    Binning, BinningLUT,
    PixelType, PixelTypeLUT, AcquisitionState, BitPackingMode
)
from voxel.devices.utils.singleton import Singleton
from voxel.devices.utils.geometry import Vec2D

# dcam properties dict for convenience in calls
PROPERTIES = {
    # TODO: Figure out the use of subarray_mode
    "subarray_mode": 4202832,  # 0x00402150, R/W, mode, "SUBARRAY MODE"
    "sensor_temperature": 2097936,  # 0x00200310, R/O, celsius, "TEMPERATURE"
}

DELIMINATED_PROPERTIES = {
    "exposure_time_s": 2031888,  # 0x001F0110, R/W, sec, "EXPOSURE TIME"
    "line_interval_s": 4208720,  # 0x00403850, R/W, sec, "INTERNAL LINE INTERVAL"
    "image_width_px": 4325904,  # 0x00420210, R/O, long, "IMAGE WIDTH"
    "image_height_px": 4325920,  # 0x00420220, R/O, long, "IMAGE HEIGHT"
    "roi_width_px": 4202784,  # 0x00402120, R/W, long, "SUBARRAY HSIZE"
    "roi_height_px": 4202816,  # 0x00402140, R/W, long, "SUBARRAY VSIZE"
    "roi_width_offset_px": 4202768,  # 0x00402110, R/W, long, "SUBARRAY HPOS"
    "roi_height_offset_px": 4202800,  # 0x00402130, R/W, long, "SUBARRAY VPOS"
}

ENUMERATED_PROPERTIES = {
    "pixel_type": 4326000,  # 0x00420270, R/W, DCAM_PIXELTYPE, "PIXEL TYPE"
    "binning": 4198672,  # 0x00401110, R/W, mode, "BINNING"
    "sensor_mode": 4194832,  # 0x00400210, R/W, mode,  "SENSOR MODE"
    "readout_direction": 4194608,  # 0x00400130, R/W, mode, "READOUT DIRECTION"
    "trigger_active": 1048864,  # 0x00100120, R/W, mode, "TRIGGER ACTIVE"
    "trigger_mode": 1049104,  # 0x00100210, R/W, mode, "TRIGGER MODE"
    "trigger_polarity": 1049120,  # 0x00100220, R/W, mode, "TRIGGER POLARITY"
    "trigger_source": 1048848,  # 0x00100110, R/W, mode, "TRIGGER SOURCE"
}

LimitType = Literal['min', 'max', 'step']
EnumeratedProp: TypeAlias = Union[
    PixelType, Binning, SensorMode, ReadoutDirection,
    TriggerMode, TriggerSource, TriggerPolarity, TriggerActive
]


class DcamapiSingleton(Dcamapi, metaclass=Singleton):
    def __init__(self):
        """Singleton wrapper around the DCAM SDK. Ensures the same DCAM \n
        instance is returned anytime DCAM is initialized.
        """
        super(DcamapiSingleton, self).__init__()


def discover_dcam(provider: Dcamapi, serial_number: str) -> Tuple[Dcam, int]:
    """Discover the camera with the given serial number.

    :param provider: The DCAM Api object.
    :param serial_number: The serial number of the camera.
    :type provider: Dcamapi
    :type serial_number: str
    :return: The camera object and the camera index (for resetting the camera)
    :rtype: Tuple[Dcam, int]
    :raises DeviceConnectionError: Failed to discover camera.
    """
    try:
        provider.init()
        num_cams = provider.get_devicecount()
        serial_numbers = []
        for cam_num in range(0, num_cams):
            dcam = Dcam(cam_num)
            cam_id = dcam.dev_getstring(DCAM_IDSTR.CAMERAID)
            serial_numbers.append(cam_id.replace("S/N: ", ""))
            if cam_id.replace("S/N: ", "") == serial_number:
                return dcam, cam_num
        raise DeviceConnectionError(
            f"Camera with serial number {serial_number} not found."
            f" Found cameras: {serial_numbers}"
        )
    except Exception as e:
        raise DeviceConnectionError(
            f"Failed to discover camera. DcamapiSingleton.init() fails with error {DCAMERR(provider.lasterr()).name}"
        ) from e


# TODO: FIgure out how to do resets on dcam instances
def reset_dcam(provider: Dcamapi, dcam_idx: int) -> Dcam:
    """Reset the camera to its default state.

    :param provider: The DCAM Api object.
    :param dcam_idx: The camera index.
    :type provider: Dcamapi
    :type dcam_idx: int
    :raises DeviceConnectionError: Failed to reset camera.
    """
    try:
        dcam = Dcam(dcam_idx)
        dcam.dev_open()
        dcam.dev_close()
        return dcam
    except Exception as e:
        raise DeviceConnectionError(
            "Failed to reset camera. "
            "DcamapiSingleton.init() fails with error {}"
            .format(DCAMERR(provider.lasterr()))) from e


class HamamatsuCamera(VoxelCamera):
    """Voxel driver for Hamamatsu cameras. \n
    :param serial_number: Serial number of the camera.
    :param id: Unique voxel identifier for the camera. Empty string by default.
    :raises DeviceConnectionError: Failed to initialize DCAM API or no camera found.
    """

    BUFFER_SIZE_MB = 2400

    # subarray parameter values
    SUBARRAY_OFF = 1
    SUBARRAY_ON = 2

    try:
        _dcam_provider: Dcamapi = DcamapiSingleton()
    except Exception as e:
        raise DeviceConnectionError("Failed to initialize DCAM API") from e

    def __init__(self, serial_number: str, id: str = '') -> None:
        """Voxel driver for Hamamatsu cameras.

        :param id: Unique voxel identifier for the camera. Empty string by default.
        :param serial_number: Serial number of the camera.
        :type id: str
        :raises ValueError: No camera found.
        """
        super().__init__(id)

        self.serial_number = serial_number
        self._dcam, self._dcam_idx = discover_dcam(self._dcam_provider, self.serial_number)
        self._dcam.dev_open()
        self.log.info(f"Hamamatsu camera found with serial number: {self.serial_number}")

        # Flags
        self._buffer_allocated = False

        # Caches
        self._sensor_size_px: Optional[Vec2D] = None
        self._binning: Optional[Binning] = None

        # Bool is returned when the dcam instance is not opened. make sure dcam.dev_open() is called before accessing
        self._delimination_props: Dict[str, Optional[Union[DCAMPROP_ATTR, bool]]] = {
            "exposure_time_s": None,
            "line_interval_s": None,
            "image_width_px": None,  # image_width
            "image_height_px": None,  # image_height
            "roi_width_px": None,  # subarray_hsize
            "roi_height_px": None,  # subarray_vsize
            "roi_width_offset_px": None,  # subarray_hpos
            "roi_height_offset_px": None,  # subarray_vpos
        }
        self._fetch_all_delimination_props()

        # LUTs
        self._binning_lut: BinningLUT = self._get_binning_lut()
        self._pixel_type_lut: PixelTypeLUT = self._get_pixel_type_lut()
        self._sensor_mode_lut: SensorModeLUT = self._get_enumerated_prop_lut(
            "sensor_mode", SensorMode)
        self._readout_direction_lut: ReadoutDirectionLUT = self._get_enumerated_prop_lut(
            "readout_direction", ReadoutDirection)
        self._trigger_mode_lut: TriggerModeLUT = self._get_enumerated_prop_lut(
            "trigger_mode", TriggerMode)
        self._trigger_source_lut: TriggerSourceLUT = self._get_enumerated_prop_lut(
            "trigger_source", TriggerSource)
        self._trigger_polarity_lut: TriggerPolarityLUT = self._get_enumerated_prop_lut(
            "trigger_polarity", TriggerPolarity)
        self._trigger_active_lut: TriggerActiveLUT = self._get_enumerated_prop_lut(
            "trigger_active", TriggerActive)

    def info(self):
        return (
            f"Serial Number:        {self.serial_number}\n"
            f"Sensor Size:          {self.sensor_size_px}\n"
            f"Roi Size:             ({self.roi_width_px}, {self.roi_height_px})\n"
            f"Roi Offset:           ({self.roi_width_offset_px}, {self.roi_height_offset_px})\n"
            f"Binning:              {self.binning}\n"
            f"Image Size:           {self.image_size_px}\n"
            f"Pixel Type:           {self.pixel_type}\n"
            f"Binning LUT:          {self._binning_lut}\n"
            f"Pixel Type LUT:       {self._pixel_type_lut}\n"
            f"Sensor Mode LUT:      {self._sensor_mode_lut}\n"
            f"Readout Dir LUT:      {self._readout_direction_lut}\n"
            f"Trigger Mode LUT:     {self._trigger_mode_lut}\n"
            f"Trigger Source LUT:   {self._trigger_source_lut}\n"
            f"Trigger Polarity LUT: {self._trigger_polarity_lut}\n"
            f"Trigger Active LUT:   {self._trigger_active_lut}\n"
        )

    @property
    def sensor_size_px(self) -> Vec2D:
        """Get the sensor size in pixels.
        :return: The sensor size in pixels.
        :rtype: Vec2D
        """
        if self._sensor_size_px is None:
            self._sensor_size_px = Vec2D(
                self._get_delimination_prop_value("image_width_px"),
                self._get_delimination_prop_value("image_height_px")
            )
        return self._sensor_size_px

    # Convenience properties ##################################################
    @property
    def sensor_width_px(self) -> int:
        """Get the sensor width in pixels.
        :return: The sensor width in pixels.
        :rtype: int
        """
        return self.sensor_size_px.x

    @property
    def sensor_height_px(self) -> int:
        """Get the sensor height in pixels.
        :return: The sensor height in pixels.
        :rtype: int
        """
        return self.sensor_size_px.y

    ###########################################################################

    @enumerated_property(
        enum_class=Binning,
        options_getter=lambda self: {k: k.name for k in self._binning_lut.keys()}
    )
    def binning(self) -> Binning:
        """Get the binning value.
        :return: The binning value.
        :rtype: Binning
        """
        if self._binning is None:
            self._binning = self._get_enumerated_prop_value("binning", self._binning_lut)
        return self._binning

    @binning.setter
    def binning(self, value: Binning) -> None:
        """Set the binning value.
        :param value: The binning value.
        :type value: Binning
        """
        self._set_enumerated_prop_value("binning", value)
        self._binning = value
        self._regenerate_binning_lut()
        self._invalidate_all_delimination_props()

    @property
    def image_size_px(self) -> Vec2D:
        """Get the image size in pixels.
        :return: The image size in pixels.
        :rtype: Vec2D
        """
        return Vec2D(
            self.roi_width_px,
            self.roi_height_px
        )

    @deliminated_property(
        minimum=lambda self: self._get_delimination_prop_limit("roi_width_px", "min"),
        maximum=lambda self: self._get_delimination_prop_limit("roi_width_px", "max"),
        step=lambda self: self._get_delimination_prop_limit("roi_width_px", "step"),
        unit="px"
    )
    def roi_width_px(self) -> int:
        """Get the region of interest width in pixels.
        :return: The region of interest width in pixels.
        :rtype: int
        """
        return int(self._get_delimination_prop_value("roi_width_px"))

    @roi_width_px.setter
    def roi_width_px(self, value: int) -> None:
        """Set the region of interest width in pixels.
        :param value: The region of interest width in pixels.
        :type value: int
        """
        self.roi_width_offset_px = 0
        self._set_delimination_prop_value("roi_width_px", value)

        # center the width
        offset = (self.sensor_size_px.x - value) // 2
        self.roi_width_offset_px = offset

        self.log.info(f"Set roi width to {value} px, offset to {offset} px")
        self._invalidate_delimination_prop("roi_width_px")

    @deliminated_property(
        minimum=0,
        maximum=lambda self: self.sensor_size_px.x - self.roi_width_px,
        step=lambda self: self._get_delimination_prop_limit("roi_width_offset_px", "step"),
        unit="px"
    )
    def roi_width_offset_px(self) -> int:
        """Get the region of interest width offset in pixels.
        :return: The region of interest width offset in pixels.
        :rtype: int
        """
        return int(self._get_delimination_prop_value("roi_width_offset_px"))

    @roi_width_offset_px.setter
    def roi_width_offset_px(self, value: int) -> None:
        """Set the region of interest width offset in pixels.
        :param value: The region of interest width offset in pixels.
        :type value: int
        """
        self._set_delimination_prop_value("roi_width_offset_px", value)
        self.log.info(f"Set roi width offset to {value} px")
        self._invalidate_delimination_prop("roi_width_offset_px")

    @deliminated_property(
        minimum=lambda self: self._get_delimination_prop_limit("roi_height_px", "min"),
        maximum=lambda self: self._get_delimination_prop_limit("roi_height_px", "max"),
        step=lambda self: self._get_delimination_prop_limit("roi_height_px", "step"),
        unit="px"
    )
    def roi_height_px(self) -> int:
        """Get the region of interest height in pixels.
        :return: The region of interest height in pixels.
        :rtype: int
        """
        return int(self._get_delimination_prop_value("roi_height_px"))

    @roi_height_px.setter
    def roi_height_px(self, value: int) -> None:
        """Set the region of interest height in pixels.
        :param value: The region of interest height in pixels.
        :type value: int
        """
        self.roi_height_offset_px = 0
        self._set_delimination_prop_value("roi_height_px", value)

        # center the height
        offset = (self.sensor_size_px.y - value) // 2
        self.roi_height_offset_px = offset

        self.log.info(f"Set roi height to {value} px, offset to {offset} px")
        self._invalidate_delimination_prop("roi_height_px")

    @deliminated_property(
        minimum=0,
        maximum=lambda self: self.sensor_size_px.y - self.roi_height_px,
        step=lambda self: self._get_delimination_prop_limit("roi_height_px", "step"),
        unit="px"
    )
    def roi_height_offset_px(self) -> int:
        """Get the region of interest height offset in pixels.
        :return: The region of interest height offset in pixels.
        :rtype: int
        """
        return int(self._get_delimination_prop_value("roi_height_offset_px"))

    @roi_height_offset_px.setter
    def roi_height_offset_px(self, value: int) -> None:
        """Set the region of interest height offset in pixels.
        :param value: The region of interest height offset in pixels.
        :type value: int
        """
        self._set_delimination_prop_value("roi_height_offset_px", value)
        self.log.info(f"Set roi height offset to {value} px")
        self._invalidate_delimination_prop("roi_height_offset_px")

    @deliminated_property(
        minimum=lambda self: self._get_delimination_prop_limit("exposure_time_s", "min") * 1e3,
        maximum=lambda self: self._get_delimination_prop_limit("exposure_time_s", "max") * 1e3,
        step=lambda self: self._get_delimination_prop_limit("exposure_time_s", "step") * 1e3,
        unit="ms"
    )
    def exposure_time_ms(self) -> int:
        """Get the exposure time in milliseconds.
        :return: The exposure time in milliseconds.
        :rtype: int
        """
        return int(self._get_delimination_prop_value("exposure_time_s") * 1e3)

    @exposure_time_ms.setter
    def exposure_time_ms(self, value: int) -> None:
        """Set the exposure time in milliseconds.
        :param value: The exposure time in milliseconds.
        :type value: int
        """
        self._set_delimination_prop_value("exposure_time_s", value * 1e-3)
        self.log.info(f"Set exposure time to {value} ms")
        self._invalidate_delimination_prop("exposure_time_s")

    @deliminated_property(
        minimum=lambda self: self._get_delimination_prop_limit("line_interval_s", "min") * 1e6,
        maximum=lambda self: self._get_delimination_prop_limit("line_interval_s", "max") * 1e6,
        step=lambda self: self._get_delimination_prop_limit("line_interval_s", "step") * 1e6,
        unit="us"
    )
    def line_interval_us(self) -> int:
        """Get the line interval in microseconds.
        :return: The line interval in microseconds.
        :rtype: int
        """
        return int(self._get_delimination_prop_value("line_interval_s") * 1e6)

    @line_interval_us.setter
    def line_interval_us(self, value: int) -> None:
        """Set the line interval in microseconds.
        :param value: The line interval in microseconds.
        :type value: int
        """
        self._set_delimination_prop_value("line_interval_s", value * 1e-6)
        self.log.info(f"Set line interval to {value} us")
        self._invalidate_delimination_prop("line_interval_s")

    # TODO: Figure out the proper implementation for frame time. does it depend on readout_mode?
    @property
    def frame_time_ms(self) -> int:
        """Get the frame time in milliseconds.
        :return: The frame time in milliseconds.
        :rtype: int
        """
        return (self.line_interval_us * self.roi_height_px) / 1e3 + self.exposure_time_ms

    @enumerated_property(
        enum_class=PixelType,
        options_getter=lambda self: {k: k.name for k in self._pixel_type_lut.keys()}
    )
    def pixel_type(self) -> PixelType:
        """Get the pixel type.
        :return: The pixel type.
        :rtype: PixelType
        """
        return self._get_enumerated_prop_value("pixel_type", self._pixel_type_lut)

    @pixel_type.setter
    def pixel_type(self, value: PixelType) -> None:
        """Set the pixel type.
        :param value: The pixel type.
        :type value: PixelType
        """
        self._set_enumerated_prop_value("pixel_type", value)
        self._regenerate_pixel_type_lut()
        self._invalidate_all_delimination_props()

    @enumerated_property(
        enum_class=SensorMode,
        options_getter=lambda self: {k: k.name for k in self._sensor_mode_lut.keys()}
    )
    def sensor_mode(self) -> SensorMode:
        """Get the sensor mode.
        :return: The sensor mode.
        :rtype: SensorMode
        """
        return self._get_enumerated_prop_value("sensor_mode", self._sensor_mode_lut)

    @sensor_mode.setter
    def sensor_mode(self, value: SensorMode) -> None:
        """Set the sensor mode.
        :param value: The sensor mode.
        :type value: SensorMode
        """
        self._set_enumerated_prop_value("sensor_mode", value)
        self._regenerate_sensor_mode_lut()
        self._invalidate_all_delimination_props()

    @enumerated_property(
        enum_class=ReadoutDirection,
        options_getter=lambda self: {k: k.name for k in self._readout_direction_lut.keys()}
    )
    def readout_direction(self) -> ReadoutDirection:
        """Get the readout direction.
        :return: The readout direction.
        :rtype: ReadoutDirection
        """
        return self._get_enumerated_prop_value("readout_direction", self._readout_direction_lut)

    @readout_direction.setter
    def readout_direction(self, value: ReadoutDirection) -> None:
        """Set the readout direction.
        :param value: The readout direction.
        :type value: ReadoutDirection
        """
        self._set_enumerated_prop_value("readout_direction", value)
        self._regenerate_readout_direction_lut()
        self._invalidate_all_delimination_props()

    @enumerated_property(
        enum_class=TriggerMode,
        options_getter=lambda self: {k: k.name for k in self._trigger_mode_lut.keys()}
    )
    def trigger_mode(self) -> TriggerMode:
        """Get the trigger mode.
        :return: The trigger mode.
        :rtype: TriggerMode
        """
        return self._get_enumerated_prop_value("trigger_mode", self._trigger_mode_lut)

    @trigger_mode.setter
    def trigger_mode(self, value: TriggerMode) -> None:
        """Set the trigger mode.
        :param value: The trigger mode.
        :type value: TriggerMode
        """
        self._set_enumerated_prop_value("trigger_mode", value)
        self._regenerate_trigger_mode_lut()
        self._invalidate_all_delimination_props()

    @enumerated_property(
        enum_class=TriggerSource,
        options_getter=lambda self: {k: k.name for k in self._trigger_source_lut.keys()}
    )
    def trigger_source(self) -> TriggerSource:
        """Get the trigger source.
        :return: The trigger source.
        :rtype: TriggerSource
        """
        return self._get_enumerated_prop_value("trigger_source", self._trigger_source_lut)

    @trigger_source.setter
    def trigger_source(self, value: TriggerSource) -> None:
        """Set the trigger source.
        :param value: The trigger source.
        :type value: TriggerSource
        """
        self._set_enumerated_prop_value("trigger_source", value)
        self._regenerate_trigger_source_lut()
        self._invalidate_all_delimination_props()

    @enumerated_property(
        enum_class=TriggerPolarity,
        options_getter=lambda self: {k: k.name for k in self._trigger_polarity_lut.keys()}
    )
    def trigger_polarity(self) -> TriggerPolarity:
        """Get the trigger polarity.
        :return: The trigger polarity.
        :rtype: TriggerPolarity
        """
        return self._get_enumerated_prop_value("trigger_polarity", self._trigger_polarity_lut)

    @trigger_polarity.setter
    def trigger_polarity(self, value: TriggerPolarity) -> None:
        """Set the trigger polarity.
        :param value: The trigger polarity.
        :type value: TriggerPolarity
        """
        self._set_enumerated_prop_value("trigger_polarity", value)
        self._regenerate_trigger_polarity_lut()
        self._invalidate_all_delimination_props()

    @enumerated_property(
        enum_class=TriggerActive,
        options_getter=lambda self: {k: k.name for k in self._trigger_active_lut.keys()}
    )
    def trigger_active(self) -> TriggerActive:
        """Get the trigger active.
        :return: The trigger active.
        :rtype: TriggerActive
        """
        return self._get_enumerated_prop_value("trigger_active", self._trigger_active_lut)

    @trigger_active.setter
    def trigger_active(self, value: TriggerActive) -> None:
        """Set the trigger active.
        :param value: The trigger active.
        :type value: TriggerActive
        """
        self._set_enumerated_prop_value("trigger_active", value)
        self._regenerate_trigger_active_lut()
        self._invalidate_all_delimination_props()

    @property
    def trigger_settings(self) -> TriggerSettings:
        """Get the trigger settings.
        :return: The trigger settings.
        :rtype: TriggerSettings
        """
        return TriggerSettings(
            mode=self.trigger_mode,
            source=self.trigger_source,
            polarity=self.trigger_polarity,
            active=self.trigger_active
        )

    @property
    def trigger(self) -> Dict:
        return self.trigger_settings.dict()

    @property
    def bit_packing_mode(self) -> BitPackingMode:
        pass

    def prepare(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def grab_frame(self) -> NDArray[np.int_]:
        pass

    @property
    def acquisition_state(self) -> AcquisitionState:
        pass

    def log_metadata(self) -> None:
        pass

    def close(self) -> None:
        if self._dcam.is_opened():
            self._dcam.dev_close()
            DcamapiSingleton.uninit()

    # Private methods ###################################################################################

    # Deliminated properties
    def _fetch_all_delimination_props(self) -> None:
        """Fetch all delimination properties."""
        for prop_name in self._delimination_props:
            self._fetch_delimination_prop(prop_name)

    def _invalidate_all_delimination_props(self) -> None:
        """Invalidate all delimination properties."""
        for prop_name in self._delimination_props:
            self._invalidate_delimination_prop(prop_name)

    def _invalidate_delimination_prop(self, prop_name: str) -> None:
        """Invalidate a delimination property.

        :param prop_name: The property name.
        :type prop_name: str
        """
        self._delimination_props[prop_name] = None
        self.log.debug(f"Invalidated delimination prop: {prop_name}")

    def _fetch_delimination_prop(self, prop_name: str) -> Union[DCAMPROP_ATTR, bool, None]:
        """Fetch the value of a delimination property.

        :param prop_name: The property name.
        :type prop_name: str
        :return: The property value.
        :rtype: float
        """
        if prop_name not in self._delimination_props:
            return None
        if self._delimination_props[prop_name] is None:
            res = self._dcam.prop_getattr(DELIMINATED_PROPERTIES[prop_name])
            if type(res) is DCAMPROP_ATTR:
                self._delimination_props[prop_name] = res
            else:
                self.log.error(f"Failed to fetch delimination prop: {prop_name}. "
                               f"Error: {DCAMERR(self._dcam_provider.lasterr())}")
        self.log.debug(f"Fetched delimination prop: {prop_name}")
        return self._delimination_props[prop_name]

    def _get_delimination_prop_limit(self, prop_name: str, limit_type: LimitType) -> Optional[float]:
        """Query the min, max, and step of a delimination property.

        :param prop_name: The property name.
        :type prop_name: str
        :param limit_type: The limit type. Either "min", "max", or "step".
        :type limit_type: Literal['min', 'max', 'step']
        :return: The property value.
        :rtype: Optional[float]
        """
        delimination_prop = self._fetch_delimination_prop(prop_name)
        try:
            match limit_type:
                case 'min':
                    return delimination_prop.valuemin
                case 'max':
                    return delimination_prop.valuemax
                case 'step':
                    return delimination_prop.valuestep
                case _:
                    self.log.error(f"Invalid limit type: {limit_type}")
                    return None
        except Exception as e:
            self.log.error(f"Failed to query delimination property: {prop_name}")
            return None

    def _get_delimination_prop_value(self, prop_name: str) -> Optional[float | int]:
        """Get the value of a delimination property.

        :param prop_name: The property name.
        :type prop_name: str
        :return: The property value.
        :rtype: Optional[float]
        """
        value = self._dcam.prop_getvalue(DELIMINATED_PROPERTIES[prop_name])
        if value is None:
            self.log.error(f"Failed to get dcam property: {prop_name}")
            return -1
        self.log.debug(f"Fetched camera property, {prop_name}: {value}")
        return value

    def _set_delimination_prop_value(self, prop_name: str, value: int | float) -> None:
        """Set the value of a delimination property.

        :param prop_name: The property name.
        :param value: The property value.
        :type prop_name: str
        :type value: int | float
        """
        self._dcam.prop_setvalue(DELIMINATED_PROPERTIES[prop_name], value)
        self.log.debug(f"Set camera property: {prop_name} to {value}")

    # Enumerated properties

    def _get_enumerated_prop_value(self, prop_name: str, lut: dict) -> EnumeratedProp:
        """Get the value of an enumerated property.

        :param prop_name: The property name.
        :param lut: The look-up table for the property.
        :type prop_name: str
        :type lut: dict
        :return: The property value.
        :rtype: Optional[int]
        """
        prop_value = self._dcam.prop_getvalue(ENUMERATED_PROPERTIES[prop_name])
        default = next(iter(lut.keys()))  # First key in the lut
        if prop_value is None:
            self.log.error(f"Failed to get dcam property: {prop_name}")
            # TODO: Figure out how to handle lut lookups when the property value is None
            return default
        self.log.debug(f"Fetched camera property, {prop_name}: {prop_value}")
        return lut.get(prop_value, default)

    def _set_enumerated_prop_value(self, prop_name: str, value: int) -> None:
        """Set the value of an enumerated property.

        :param prop_name: The property name.
        :param value: The property value.
        :type prop_name: str
        :type value: int
        """
        self._dcam.prop_setvalue(ENUMERATED_PROPERTIES[prop_name], value)
        self.log.debug(f"Set camera property: {prop_name} to {value}")

    def _get_enumerated_prop_lut(self, prop_name: str, enum_class) -> dict:
        """Get the look-up table for an enumerated property.

        :param prop_name: The property name.
        :type prop_name: str
        :return: The look-up table.
        :rtype: dict
        """
        lut = {}
        prop_attr = self._dcam.prop_getattr(ENUMERATED_PROPERTIES[prop_name])
        self.log.info(f"{prop_name} attribute: {prop_attr}")
        if type(prop_attr) is DCAMPROP_ATTR:
            for prop_value in range(int(prop_attr.valuemin), int(prop_attr.valuemax + 1)):
                reply = self._dcam.prop_getvaluetext(ENUMERATED_PROPERTIES[prop_name], prop_value)
                if reply:
                    lut_key = reply.upper().replace(" ", "")
                    lut[enum_class[lut_key]] = prop_value
        return lut

    def _get_binning_lut(self) -> BinningLUT:
        """Generate the binning look-up table.
        Query dcam to determine the range of binning values and create a look-up table.

        :return: The binning look-up table.
        :rtype: BinningLUT
        """
        lut: BinningLUT = {}
        binning_attr: DCAMPROP_ATTR = self._dcam.prop_getattr(ENUMERATED_PROPERTIES["binning"])
        self.log.info(f"Binning attribute: {binning_attr}")
        if type(binning_attr) is DCAMPROP_ATTR:
            for prop_value in range(int(binning_attr.valuemin), int(binning_attr.valuemax + 1)):
                reply = self._dcam.prop_getvaluetext(ENUMERATED_PROPERTIES["binning"], prop_value)
                if reply:
                    lut[Binning[reply.upper()[1:]]] = prop_value
        return lut

    def _get_pixel_type_lut(self) -> PixelTypeLUT:
        """Generate the pixel type look-up table.
        Query dcam to determine the range of pixel types and create a look-up table.

        :return: The pixel type look-up table.
        :rtype: PixelTypeLUT
        """
        lut: PixelTypeLUT = {}
        pixel_type_attr: DCAMPROP_ATTR = self._dcam.prop_getattr(ENUMERATED_PROPERTIES["pixel_type"])
        self.log.info(f"Pixel type attribute: {pixel_type_attr}")
        if type(pixel_type_attr) is DCAMPROP_ATTR:
            for prop_value in range(int(pixel_type_attr.valuemin), int(pixel_type_attr.valuemax + 1)):
                reply = self._dcam.prop_getvaluetext(ENUMERATED_PROPERTIES["pixel_type"], prop_value)
                if reply:
                    lut[PixelType[reply]] = prop_value
        return lut

    def _regenerate_all_luts(self) -> None:
        """Regenerate all look-up tables."""
        self._regenerate_binning_lut()
        self._regenerate_pixel_type_lut()
        self._regenerate_sensor_mode_lut()
        self._regenerate_readout_direction_lut()
        self._regenerate_trigger_mode_lut()
        self._regenerate_trigger_source_lut()
        self._regenerate_trigger_polarity_lut()
        self._regenerate_trigger_active_lut()

    def _regenerate_binning_lut(self) -> None:
        """Regenerate the binning look-up table."""
        self._binning_lut = self._get_binning_lut()

    def _regenerate_pixel_type_lut(self) -> None:
        """Regenerate the pixel type look-up table."""
        self._pixel_type_lut = self._get_pixel_type_lut()

    def _regenerate_sensor_mode_lut(self) -> None:
        """Regenerate the sensor mode look-up table."""
        self._sensor_mode_lut = self._get_enumerated_prop_lut("sensor_mode", SensorMode)

    def _regenerate_readout_direction_lut(self) -> None:
        """Regenerate the readout direction look-up table."""
        self._readout_direction_lut = self._get_enumerated_prop_lut("readout_direction", ReadoutDirection)

    def _regenerate_trigger_mode_lut(self) -> None:
        """Regenerate the trigger mode look-up table."""
        self._trigger_mode_lut = self._get_enumerated_prop_lut("trigger_mode", TriggerMode)

    def _regenerate_trigger_source_lut(self) -> None:
        """Regenerate the trigger source look-up table."""
        self._trigger_source_lut = self._get_enumerated_prop_lut("trigger_source", TriggerSource)

    def _regenerate_trigger_polarity_lut(self) -> None:
        """Regenerate the trigger polarity look-up table."""
        self._trigger_polarity_lut = self._get_enumerated_prop_lut("trigger_polarity", TriggerPolarity)

    def _regenerate_trigger_active_lut(self) -> None:
        """Regenerate the trigger active look-up table."""
        self._trigger_active_lut = self._get_enumerated_prop_lut("trigger_active", TriggerActive)

    # Might not be needed
    def _get_sensor_mode_lut(self) -> SensorModeLUT:
        """Generate the sensor mode look-up table.
        Query dcam to determine the range of sensor modes and create a look-up table.

        :return: The sensor mode look-up table.
        :rtype: SensorModeLUT
        """
        lut: SensorModeLUT = {}
        sensor_mode_attr: DCAMPROP_ATTR = self._dcam.prop_getattr(ENUMERATED_PROPERTIES["sensor_mode"])
        self.log.info(f"Sensor mode attribute: {sensor_mode_attr}")
        if type(sensor_mode_attr) is DCAMPROP_ATTR:
            for prop_value in range(int(sensor_mode_attr.valuemin), int(sensor_mode_attr.valuemax + 1)):
                reply = self._dcam.prop_getvaluetext(ENUMERATED_PROPERTIES["sensor_mode"], prop_value)
                if reply:
                    lut[SensorMode[reply.upper().replace(" ", "")]] = prop_value
        return lut

    def _get_readout_direction_lut(self) -> ReadoutDirectionLUT:
        """Generate the readout direction look-up table.
        Query dcam to determine the range of readout directions and create a look-up table.

        :return: The readout direction look-up table.
        :rtype: ReadoutDirectionLUT
        """
        lut: ReadoutDirectionLUT = {}
        readout_direction_attr: DCAMPROP_ATTR = self._dcam.prop_getattr(ENUMERATED_PROPERTIES["readout_direction"])
        self.log.info(f"Readout direction attribute: {readout_direction_attr}")
        if type(readout_direction_attr) is DCAMPROP_ATTR:
            for prop_value in range(int(readout_direction_attr.valuemin), int(readout_direction_attr.valuemax + 1)):
                reply = self._dcam.prop_getvaluetext(ENUMERATED_PROPERTIES["readout_direction"], prop_value)
                if reply:
                    lut[ReadoutDirection[reply.upper().replace(" ", "")]] = prop_value
        return lut
