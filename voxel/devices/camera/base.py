from abc import abstractmethod

import numpy as np
from numpy.typing import NDArray

from voxel.descriptors.deliminated_property import deliminated_property
from voxel.devices.camera.typings import TriggerSettingsLUT, PixelTypeLUT, BinningLUT, BitPackingModeLUT, PixelType, \
    BitPackingMode, TriggerSettings, AcquisitionState, Binning
from voxel.devices.base import VoxelDevice
from voxel.devices.utils.geometry import Vec2D


class VoxelCamera(VoxelDevice):
    """Base class for all voxel supported cameras."""

    def __init__(self, id: str):
        """Initialize the camera.

        :param id: The unique identifier of the camera.
        :type id: str
        """
        super().__init__(id)

    # ROI Configuration Properties
    @deliminated_property()
    @abstractmethod
    def roi_width_px(self) -> int:
        """Get the width of the camera region of interest in pixels.

        :return: The width of the region of interest in pixels.
        :rtype: int
        """
        pass

    @roi_width_px.setter
    @abstractmethod
    def roi_width_px(self, width_px: int) -> None:
        """Set the width of the camera region of interest in pixels.

        :param width_px: The width of the region of interest in pixels.
        :type width_px: int
        """
        pass

    @property
    @abstractmethod
    def roi_width_offset_px(self) -> int:
        """Get the width offset of the camera region of interest in pixels.

        :return: The width offset of the region of interest in pixels.
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def sensor_width_px(self) -> int:
        """Get the width of the camera sensor in pixels.

        :return: The width of the camera sensor in pixels.
        :rtype: int
        """
        pass

    @deliminated_property()
    @abstractmethod
    def roi_height_px(self) -> int:
        """Get the height of the camera region of interest in pixels.

        :return: The height of the region of interest in pixels.
        :rtype: int
        """
        pass

    @roi_height_px.setter
    @abstractmethod
    def roi_height_px(self, height_px: int, center=True) -> None:
        """Set the height of the camera region of interest in pixels.

        :param height_px: The height of the region of interest in pixels.
        :param center: Whether to center the ROI
        :type height_px: int
        :type center: bool
        """
        pass

    @property
    @abstractmethod
    def roi_height_offset_px(self) -> int:
        """Get the height offset of the camera region of interest in pixels.

        :return: The height offset of the region of interest in pixels.
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def sensor_height_px(self) -> int:
        """Get the height of the camera sensor in pixels.

        :return: The height of the camera sensor in pixels.
        :rtype: int
        """
        pass

    # Image Format Properties
    @property
    @abstractmethod
    def binning(self) -> Binning:
        """Get the binning mode of the camera. \n
        Integer value, e.g. 2 is 2x2 binning

        :return: The binning mode of the camera
        :rtype: int
        """
        pass

    @binning.setter
    @abstractmethod
    def binning(self, binning: Binning) -> None:
        """Set the binning mode of the camera. \n
        Integer value, e.g. 2 is 2x2 binning

        :param binning: The binning mode of the camera
        :type binning: int
        """
        pass

    @property
    @abstractmethod
    def image_size_px(self) -> Vec2D:
        """Get the size of the camera image in pixels.

        :return: The size of the camera image in pixels.
        :rtype: Vec2D
        """
        pass

    @property
    @abstractmethod
    def pixel_type(self) -> PixelType:
        """Get the pixel type of the camera.

        :return: The pixel type of the camera.
        :rtype: PixelType
        """
        pass

    @pixel_type.setter
    @abstractmethod
    def pixel_type(self, pixel_type_bits: PixelType) -> None:
        """The pixel type of the camera: \n
        - mono8, mono10, mono12, mono14, monospacing, etc.

        :param pixel_type_bits: The pixel type
        :type pixel_type_bits: PixelType
        """
        pass

    @property
    @abstractmethod
    def bit_packing_mode(self) -> BitPackingMode:
        """Get the bit packing mode of the camera.

        :return: The bit packing mode of the camera.
        :rtype: BitPackingMode
        """
        pass

    @bit_packing_mode.setter
    @abstractmethod
    def bit_packing_mode(self, bit_packing: BitPackingMode) -> None:
        """The bit packing mode of the camera: \n
        - lsb, msb, none

        :param bit_packing: The bit packing mode
        :type bit_packing: BitPackingMode
        """
        pass

    # Acquisition/Capture Properties
    @deliminated_property()
    @abstractmethod
    def exposure_time_ms(self) -> float:
        """Get the exposure time of the camera in ms.

        :return: The exposure time in ms.
        :rtype: float
        """
        pass

    @exposure_time_ms.setter
    @abstractmethod
    def exposure_time_ms(self, exposure_time_ms: float) -> None:
        """Set the exposure time of the camera in ms.

        :param exposure_time_ms: The exposure time in ms.
        :type exposure_time_ms: float
        """
        pass

    @property
    @abstractmethod
    def line_interval_us(self) -> float:
        """Get the line interval of the camera in us. \n
        This is the time interval between adjacent \n
        rows activating on the camera sensor.

        :return: The line interval of the camera in us
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def frame_time_ms(self) -> float:
        """Get the frame time of the camera in ms. \n
        This is the total time to acquire a single image

        :return: The frame time of the camera in ms
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def trigger(self) -> TriggerSettings:
        """Get the trigger mode of the camera. \n
        The trigger mode consists of three parameters: \n
        - mode (e.g. on or off) \n
        - source (e.g. internal or external) \n
        - polarity (e.g. rising edge or falling edge)

        :return: The trigger mode of the camera.
        :rtype: TriggerSettings
        """
        pass

    @trigger.setter
    @abstractmethod
    def trigger(self, trigger: TriggerSettings) -> None:
        """Set the trigger mode of the camera. \n
        The trigger mode consists of three parameters: \n
        - mode (e.g. on or off) \n
        - source (e.g. internal or external) \n
        - polarity (e.g. rising edge or falling edge)

        :param trigger: The trigger mode of the camera
        :type trigger: dict
        """
        pass

    @abstractmethod
    def prepare(self) -> None:
        """Prepare the camera to acquire images. \n
        Initializes the camera buffer.
        """
        pass

    @abstractmethod
    def start(self, frame_count: int) -> None:
        """Start the camera to acquire a certain number of frames. \n
        If frame number is not specified, acquires infinitely until stopped. \n
        Initializes the camera buffer.

        :param frame_count: The number of frames to acquire
        :type frame_count: int
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the camera."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the camera."""
        pass

    @abstractmethod
    def grab_frame(self) -> NDArray[np.int_]:
        """Grab a frame from the camera buffer. \n
        If binning is via software, the GPU binned \n
        image is computed and returned.

        :return: The camera frame of size (height, width).
        :rtype: NDArray[np.int_]
        """
        pass

    @property
    @abstractmethod
    def acquisition_state(self) -> AcquisitionState:
        """Return a dictionary of the acquisition state: \n
        - Frame Index - frame number of the acquisition \n
        - Input Buffer Size - number of free frames in buffer \n
        - Output Buffer Size - number of frames to grab from buffer \n
        - Dropped Frames - number of dropped frames
        - Data Rate [MB/s] - data rate of acquisition
        - Frame Rate [fps] - frames per second of acquisition

        :return: The acquisition state
        :rtype: AcquisitionState
        """
        pass

    # TODO: Determine whether to have signals as abstract properties that must be implemented by the child class
    #  or as methods that can be implemented by the child class
    #  or leave it to the discretion of the child class to add whatever signals they want
    # @property
    # @abstractmethod
    # def signal_mainboard_temperature_c(self) -> float:
    #     """Get the mainboard temperature of the camera in deg C.

    #     :return: The mainboard temperature of the camera in deg C.
    #     :rtype: float
    #     """
    #     pass

    # @property
    # # @abstractmethod
    # def signal_sensor_temperature_c(self) -> float:
    #     """
    #     Get the sensor temperature of the camera in deg C.

    #     :return: The sensor temperature of the camera in deg C.
    #     :rtype: float
    #     """
    #     pass

    @abstractmethod
    def log_metadata(self) -> None:
        """Log all metadata from the camera to the logger."""
        pass

    def __repr__(self):
        properties = [
            f"ID: {self.id}",
            f"Sensor: {self.sensor_width_px} x {self.sensor_height_px}",
            f"ROI: {self.roi_width_px} x {self.roi_height_px}",
            f"ROI Offset: ({self.roi_width_offset_px}, {self.roi_height_offset_px})",
            f"Image Size: ({self.image_size_px.x}, {self.image_size_px.y})",
            f"Binning: {self.binning}",
            f"Pixel Type: {self.pixel_type}",
            f"Bit Packing: {self.bit_packing_mode}",
            f"Exposure: {self.exposure_time_ms:.2f} ms",
            # f"Line Interval: {self.line_interval_us:.2f} µs",
            # f"Frame Time: {self.frame_time_ms:.2f} ms",
            f"Trigger: {self.trigger}",
            # f"Readout: {self.readout_mode}"
        ]

        return f"{self.__class__.__name__}:\n" + "\n".join(f"  {prop}" for prop in properties)


