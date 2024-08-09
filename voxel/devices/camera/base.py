from abc import abstractmethod

import numpy as np
from numpy.typing import NDArray

from voxel.descriptors.deliminated_property import DeliminatedProperty
from voxel.devices.device import VoxelDevice


class BaseCamera(VoxelDevice):
    """Base class for all voxel supported cameras."""

    @DeliminatedProperty
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

    @DeliminatedProperty
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

    @DeliminatedProperty
    @abstractmethod
    def roi_height_px(self) -> int:
        """Get the height of the camera region of interest in pixels.

        :return: The height of the region of interest in pixels.
        :rtype: int
        """
        pass

    @roi_height_px.setter
    @abstractmethod
    def roi_height_px(self, height_px: int) -> None:
        """Set the height of the camera region of interest in pixels.

        :param height_px: The height of the region of interest in pixels.
        :type height_px: int
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
    def pixel_type(self) -> str:
        """Get the pixel type of the camera.

        :return: The pixel type of the camera.
        :rtype: str
        """
        pass

    @pixel_type.setter
    @abstractmethod
    def pixel_type(self, pixel_type_bits: str) -> None:
        """The pixel type of the camera: \n
        - mono8, mono10, mono12, mono14, mono16, etc.

        :param pixel_type_bits: The pixel type
        :type pixel_type_bits: str
        """
        pass

    @property
    @abstractmethod
    def bit_packing_mode(self) -> str:
        """Get the bit packing mode of the camera.

        :return: The bit packing mode of the camera.
        :rtype: str
        """
        pass

    @bit_packing_mode.setter
    @abstractmethod
    def bit_packing_mode(self, bit_packing: str) -> None:
        """The bit packing mode of the camera: \n
        - lsb, msb, none

        :param bit_packing: The bit packing mode
        :type bit_packing: str
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
    def trigger(self) -> dict:
        """Get the trigger mode of the camera. \n
        The trigger mode consists of three parameters: \n
        - mode (e.g. on or off) \n
        - source (e.g. internal or external) \n
        - polarity (e.g. rising edge or falling edge)

        :return: The trigger mode of the camera.
        :rtype: dict
        """
        pass

    @trigger.setter
    @abstractmethod
    def trigger(self, trigger: dict) -> None:
        """Set the trigger mode of the camera. \n
        The trigger mode consists of three parameters: \n
        - mode (e.g. on or off) \n
        - source (e.g. internal or external) \n
        - polarity (e.g. rising edge or falling edge)

        :param trigger: The trigger mode of the camera
        :type trigger: dict
        """
        pass

    @property
    @abstractmethod
    def binning(self) -> int:
        """Get the binning mode of the camera. \n
        Integer value, e.g. 2 is 2x2 binning

        :return: The binning mode of the camera
        :rtype: int
        """
        pass

    @binning.setter
    @abstractmethod
    def binning(self, binning: int) -> None:
        """Set the binning mode of the camera. \n
        Integer value, e.g. 2 is 2x2 binning

        :param binning: The binning mode of the camera
        :type binning: int
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

    @property
    @abstractmethod
    def readout_mode(self) -> str:
        """Get the readout mode of the camera.

        :return: The readout mode of the camera.
        :rtype: str
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
    def signal_acquisition_state(self) -> dict:
        """Return a dictionary of the acquisition state: \n
        - Frame Index - frame number of the acquisition \n
        - Input Buffer Size - number of free frames in buffer \n
        - Output Buffer Size - number of frames to grab from buffer \n
        - Dropped Frames - number of dropped frames
        - Data Rate [MB/s] - data rate of acquisition
        - Frame Rate [fps] - frames per second of acquisition

        :return: The acquisition state
        :rtype: dict
        """
        pass

    @abstractmethod
    def log_metadata(self) -> None:
        """Log all metadata from the camera to the logger."""
        pass
