from abc import abstractmethod
from typing import Any

from voxel.descriptors.enumerated_property import enumerated_property
from voxel.devices.camera.definitions import PixelType, AcquisitionState, Binning, VoxelFrame, ROI
from voxel.utils.geometry import Vec2D

from voxel.descriptors.deliminated_property import deliminated_property
from voxel.devices.base import VoxelDevice


class VoxelCamera(VoxelDevice):
    """Base class for all voxel supported cameras."""

    def __init__(self, id: str):
        """Initialize the camera.

        :param id: The unique identifier of the camera.
        :type id: str
        """
        super().__init__(id)

    # sensor properties
    @property
    @abstractmethod
    def sensor_size_px(self) -> Vec2D:
        """Get the size of the camera sensor in pixels.

        :return: The size of the camera sensor in pixels.
        :rtype: Vec2D
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

    @property
    @abstractmethod
    def sensor_height_px(self) -> int:
        """Get the height of the camera sensor in pixels.

        :return: The height of the camera sensor in pixels.
        :rtype: int
        """
        pass

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

    @deliminated_property()
    @abstractmethod
    def roi_width_offset_px(self) -> int:
        """Get the width offset of the camera region of interest in pixels.

        :return: The width offset of the region of interest in pixels.
        :rtype: int
        """
        pass

    @roi_width_offset_px.setter
    @abstractmethod
    def roi_width_offset_px(self, width_offset_px: int) -> None:
        """Set the width offset of the camera region of interest in pixels.
        :param width_offset_px: The width offset of the region of interest in pixels.
        :type width_offset_px: int
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

    @deliminated_property()
    @abstractmethod
    def roi_height_offset_px(self) -> int:
        """Get the height offset of the camera region of interest in pixels.

        :return: The height offset of the region of interest in pixels.
        :rtype: int
        """
        pass

    @roi_height_offset_px.setter
    @abstractmethod
    def roi_height_offset_px(self, height_offset_px: int) -> None:
        """Set the height offset of the camera region of interest in pixels.

        :param height_offset_px: The height offset of the region of interest in pixels.
        :type height_offset_px: int
        """
        pass

    @property
    def roi(self) -> ROI:
        """Get the region of interest of the camera in pixels.

        :return: The region of interest of the camera in pixels. (size, origin)
        :rtype: ROI
        """
        return ROI(
            origin=Vec2D(self.roi_width_offset_px, self.roi_height_offset_px),
            size=Vec2D(self.roi_width_px, self.roi_height_px),
            bounds=Vec2D(self.sensor_width_px, self.sensor_height_px)
        )

    def reset_roi(self) -> None:
        """Reset the ROI to full sensor size."""
        self.roi_width_offset_px = 0
        self.roi_height_offset_px = 0
        self.roi_width_px = self.sensor_size_px.x
        self.roi_height_px = self.sensor_size_px.y

    # Image Format Properties
    @enumerated_property(Binning)
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
    def frame_size_px(self) -> Vec2D:
        """Get the size of the camera image in pixels.

        :return: The size of the camera image in pixels.
        :rtype: Vec2D
        """
        pass

    @property
    @abstractmethod
    def frame_width_px(self) -> int:
        """Get the width of the camera image in pixels.

        :return: The width of the camera image in pixels.
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def frame_height_px(self) -> int:
        """Get the height of the camera image in pixels.

        :return: The height of the camera image in pixels.
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def frame_size_mb(self) -> float:
        """Get the size of the camera image in MB.

        :return: The size of the camera image in MB.
        :rtype: float
        """
        pass

    @enumerated_property(PixelType)
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
    def trigger_settings(self) -> Any:
        """
        Get the trigger settings of the camera.
        Notes:
            Parameters vary depending on the camera model.
            For example, Vieworks cameras have trigger settings
                - mode ( 'On' or 'Off' )
                - source ( 'Internal' or 'External' )
                - polarity ( 'Rising Edge' or 'Falling Edge' )
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

    @property
    @abstractmethod
    def latest_frame(self):
        """Get the latest Frame"""

    @abstractmethod
    def grab_frame(self) -> VoxelFrame:
        """Grab a frame from the camera buffer. \n
        If binning is via software, the GPU binned \n
        image is computed and returned.

        :return: The camera frame of size (height, width).
        :rtype: VoxelFrame
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

    @abstractmethod
    def log_metadata(self) -> None:
        """Log all metadata from the camera to the logger."""
        pass

    @property
    @abstractmethod
    def sensor_temperature_c(self) -> float:
        """
        Get the sensor temperature of the camera in deg C.

        :return: The sensor temperature of the camera in deg C.
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def mainboard_temperature_c(self) -> float:
        """Get the mainboard temperature of the camera in deg C.

        :return: The mainboard temperature of the camera in deg C.
        :rtype: float
        """
        pass

    def __repr__(self):
        properties = [
            f"ID: {self.id}",
            f"Sensor: {self.sensor_width_px} x {self.sensor_height_px}",
            f"ROI: {self.roi_width_px} x {self.roi_height_px}",
            f"ROI Offset: ({self.roi_width_offset_px}, {self.roi_height_offset_px})",
            f"Image Size: ({self.frame_size_px.x}, {self.frame_size_px.y})",
            f"Binning: {self.binning}",
            f"Pixel Type: {self.pixel_type}",
            f"Exposure: {self.exposure_time_ms:.2f} ms",
            f"Line Interval: {self.line_interval_us:.2f} µs",
            f"Frame Time: {self.frame_time_ms:.2f} ms",
            f"Trigger: {self.trigger_settings}",
        ]

        return f"{self.__class__.__name__}:\n" + "\n".join(f"  {prop}" for prop in properties)
