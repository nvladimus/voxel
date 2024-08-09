import time
from dataclasses import dataclass
from multiprocessing import Event
from threading import Thread

import numpy as np
from numpy.typing import NDArray

from voxel.descriptors.deliminated_property import DeliminatedProperty
from voxel.devices.camera.base import BaseCamera
from voxel.processes.gpu.gputools.downsample_2d import DownSample2D

BUFFER_SIZE_FRAMES = 8
MIN_WIDTH_PX = 64
MAX_WIDTH_PX = 14192
STEP_WIDTH_PX = 16
MIN_HEIGHT_PX = 2
MAX_HEIGHT_PX = 10640
STEP_HEIGHT_PX = 2
MIN_EXPOSURE_TIME_MS = 0.001
MAX_EXPOSURE_TIME_MS = 6e4
STEP_EXPOSURE_TIME_MS = 1

BINNING = {1: 1, 2: 2, 4: 4}

PIXEL_TYPES = {"mono8": "uint8", "mono16": "uint16"}

LINE_INTERVALS_US = {"mono8": 10.00, "mono16": 20.00}

TRIGGERS = {
    "mode": {
        "on": "On",
        "off": "Off",
    },
    "source": {
        "internal": "None",
        "external": "Line0",
    },
    "polarity": {
        "rising": "RisingEdge",
        "falling": "FallingEdge",
    },
}


@dataclass
class Plane:
    width: int | float
    height: int | float

    def __mul__(self, other):
        if isinstance(other, Plane):
            return Plane(self.width * other.width, self.height * other.height)
        if isinstance(other, int):
            return Plane(self.width * other, self.height * other)

    def __truediv__(self, other):
        return Plane(self.width / other, self.height / other)

    def __floordiv__(self, other):
        return Plane(self.width // other, self.height // other)


class SimulatedCamera(BaseCamera):
    """Voxel driver for a simulated camera. Camera constants are for a \n
    Vieworks VP-151MX camera.

    :param id: Serial number of the camera.
    :type id: str
    """

    def __init__(self, id: str, serial_number: str):
        """Constructor for the SimulatedCamera class."""
        super().__init__(id)
        self.serial_number = serial_number
        self.terminate_frame_grab = Event()
        self.terminate_frame_grab.clear()
        self._pixel_type = "mono16"
        self._line_interval_us = LINE_INTERVALS_US[self._pixel_type]
        self._exposure_time_ms = 10
        self._width_px = MAX_WIDTH_PX
        self._height_px = MAX_HEIGHT_PX
        self._width_offset_px = 0
        self._height_offset_px = 0
        self._binning = 1
        self._trigger = {"mode": "on", "source": "internal", "polarity": "rising"}

        self.gpu_binning = DownSample2D(binning=self._binning)
        self.buffer = list()
        self.thread = None

    # Image size properties  ########################################################
    @property
    def binning(self) -> int:
        """Get the binning mode of the camera. \n
        Integer value, e.g. 2 is 2x2 binning

        :return: The binning mode of the camera
        :rtype: int
        """

        return self._binning

    @binning.setter
    def binning(self, binning: int) -> None:
        """Set the binning of the camera. \n
        If the binning is not supported in hardware \n
        it will be implemented via software using the GPU. \n
        This API assumes identical binning in X and Y.

        :param binning: The binning mode of the camera
        * **1**
        * **2**
        * **4**
        :type binning: int
        :raises ValueError: Invalid binning setting
        """

        valid_binning = list(BINNING.keys())
        if binning not in valid_binning:
            raise ValueError("binning must be one of %r." % BINNING)
        else:
            self._binning = BINNING[binning]
            # initialize the downsampling in 2d
            self.gpu_binning = DownSample2D(binning=self._binning)

    @property
    def sensor_width_px(self) -> int:
        """Get the width of the camera sensor in pixels.

        :return: The width of the camera sensor in pixels
        :rtype: int
        """

        return MAX_WIDTH_PX

    @DeliminatedProperty(minimum=MIN_WIDTH_PX, maximum=MAX_WIDTH_PX, step=STEP_WIDTH_PX, unit="px")
    def roi_width_px(self) -> int:
        """Get the width of the camera region of interest in pixels.

        :return: The width of the region of interest in pixels
        :rtype: int
        """
        self.log.debug(f"getting width: {self._width_px}")
        return self._width_px

    @roi_width_px.setter
    def roi_width_px(self, value: int) -> None:
        """Set the width of the camera region of interest in pixels.

        :param value: The width of the region of interest in pixels
        :type value: int
        """
        self.log.debug(f"setting width: {value}")
        self._width_px = value
        centered_offset_px = (
                round((MAX_WIDTH_PX / 2 - value / 2) / STEP_WIDTH_PX) * STEP_WIDTH_PX
        )
        self._width_offset_px = centered_offset_px
        self.log.info(f"width set to: {value} px")

    @property
    def roi_width_offset_px(self) -> int:
        """
        Get the width offset of the camera region of interest in pixels.

        :return: The width offset of the region of interest in pixels
        :rtype: int
        """
        return self._width_offset_px

    @property
    def image_width_px(self) -> int:
        """Get the width of the camera image in pixels.

        :return: The width of the camera image in pixels
        :rtype: int
        """
        return self._width_px // self._binning

    @property
    def sensor_height_px(self) -> int:
        """Get the height of the camera sensor in pixels.

        :return: The height of the camera sensor in pixels
        :rtype: int
        """

        return MAX_HEIGHT_PX

    @DeliminatedProperty(minimum=MIN_HEIGHT_PX, maximum=MAX_HEIGHT_PX, step=STEP_HEIGHT_PX, unit="px")
    def roi_height_px(self) -> int:
        """
        Get the height of the camera region of interest in pixels.

        :return: The height of the region of interest in pixels
        :rtype: int
        """
        self.log.debug(f"getting height: {self._height_px}")
        return self._height_px

    @roi_height_px.setter
    def roi_height_px(self, value: int) -> None:
        """
        Set the height of the camera region of interest in pixels.

        :param value: The height of the region of interest in pixels
        :type value: int
        """

        centered_offset_px = (
                round((MAX_HEIGHT_PX / 2 - value / 2) / STEP_HEIGHT_PX) * STEP_HEIGHT_PX
        )
        self._height_offset_px = centered_offset_px
        self._height_px = value
        self.log.info(f"height set to: {value} px")

    @property
    def roi_height_offset_px(self) -> int:
        """Get the height offset of the camera region of interest in pixels.

        :return: The height offset of the region of interest in pixels
        :rtype: int
        """

        return self._height_offset_px

    @property
    def image_height_px(self) -> int:
        """Get the height of the camera image in pixels.

        :return: The height of the camera image in pixels
        :rtype: int
        """
        return self._height_px // self._binning

    # Image Format Properties  ##########################################################################
    @property
    def pixel_type(self) -> str:
        """Get the pixel type of the camera.

        :return: The pixel type of the camera
        :rtype: str
        """

        pixel_type = self._pixel_type
        # invert the dictionary and find the abstracted key to output
        return next(key for key, value in PIXEL_TYPES.items() if value == pixel_type)

    @pixel_type.setter
    def pixel_type(self, pixel_type_bits: str) -> None:
        """The pixel type of the camera.

        :param pixel_type_bits: The pixel type
        * **mono8**
        * **mono16**
        :type pixel_type_bits: str
        :raises ValueError: Invalid pixel type
        """

        valid = list(PIXEL_TYPES.keys())
        if pixel_type_bits not in valid:
            raise ValueError("pixel_type_bits must be one of %r." % valid)

        self._pixel_type = PIXEL_TYPES[pixel_type_bits]
        self._line_interval_us = LINE_INTERVALS_US[pixel_type_bits]
        self.log.info(f"pixel type set_to: {pixel_type_bits}")

    @property
    def bit_packing_mode(self) -> str:
        """Get the bit packing mode of the camera.

        :return: The bit packing mode of the camera.
        :rtype: str
        """
        return ""

    @bit_packing_mode.setter
    def bit_packing_mode(self, bit_packing: str) -> None:
        """The bit packing mode of the camera: \n
        - lsb, msb, none

        :param bit_packing: The bit packing mode
        :type bit_packing: str
        """
        pass

    # Acquisition Properties  ###########################################################################
    @DeliminatedProperty(
        minimum=MIN_EXPOSURE_TIME_MS, maximum=MAX_EXPOSURE_TIME_MS, step=STEP_EXPOSURE_TIME_MS, unit="ms")
    def exposure_time_ms(self) -> float:
        """Get the exposure time of the camera in ms.

        :return: The exposure time in ms
        :rtype: float
        """
        return self._exposure_time_ms

    @exposure_time_ms.setter
    def exposure_time_ms(self, exposure_time_ms: float) -> None:
        """Set the exposure time of the camera in ms.

        :param exposure_time_ms: The exposure time in ms
        :type exposure_time_ms: float
        """
        if (
                exposure_time_ms < MIN_EXPOSURE_TIME_MS
                or exposure_time_ms > MAX_EXPOSURE_TIME_MS
        ):
            self.log.warning(
                f"exposure time must be >{MIN_EXPOSURE_TIME_MS} ms \
                             and <{MAX_EXPOSURE_TIME_MS} ms. Setting exposure \
                                time to {MAX_EXPOSURE_TIME_MS} ms"
            )

        # Note: round ms to nearest us
        self._exposure_time_ms = exposure_time_ms
        self.log.info(f"exposure time set to: {exposure_time_ms} ms")

    @property
    def line_interval_us(self) -> float:
        """
        Get the line interval of the camera in us. \n
        This is the time interval between adjacnet \n
        rows activating on the camera sensor.

        :return: The line interval of the camera in us
        :rtype: float
        """

        return self._line_interval_us

    @property
    def frame_time_ms(self) -> float:
        """
        Get the frame time of the camera in ms. \n
        This is the total time to acquire a single image

        :return: The frame time of the camera in ms
        :rtype: float
        """

        return self._height_px * self._line_interval_us / 1000 + self._exposure_time_ms

    @property
    def trigger(self) -> dict:
        """
        Get the trigger mode of the camera.

        :return: The trigger mode of the camera.
        :rtype: dict
        """

        return self._trigger

    @trigger.setter
    def trigger(self, trigger: dict) -> None:
        """
        Set the trigger mode of the camera.

        :param trigger: The trigger mode of the camera
        **Trigger modes**
        * **on**
        * **off**
        **Trigger sources**
        * **line0**
        * **software**
        **Trigger polarities**
        * **risingedge**
        * **fallingedge**
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
        self._trigger = dict(trigger)

    @property
    def readout_mode(self) -> str:
        """Get the readout mode of the camera.

        :return: The readout mode of the camera.
        :rtype: str
        """
        return ""

    # Acquisition Methods  ###########################################################################
    def prepare(self):
        """
        Prepare the camera to acquire images. \n
        Initializes the camera buffer.
        """

        self.log.info("simulated camera preparing...")
        self.buffer = list()

    def start(self, frame_count: float = float("inf")):
        """
        Start the camera to acquire a certain number of frames. \n
        If frame number is not specified, acquires infinitely until stopped. \n
        Initializes the camera buffer.

        :param frame_count: The number of frames to acquire
        :type frame_count: float
        """

        self.log.info("simulated camera starting...")
        self.thread = Thread(target=self._generate_frames, args=(frame_count,))
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """
        Stop the camera.
        """

        self.log.info("simulated camera stopping...")
        self.terminate_frame_grab.set()
        self.thread.join() if self.thread else None
        self.terminate_frame_grab.clear()

    def abort(self):
        """
        Abort the camera.
        """
        self.terminate_frame_grab.set()
        if self.thread is not None:
            self.thread.join()
        self.terminate_frame_grab.clear()

    def reset(self) -> None:
        """Reset the camera."""

        self.log.info("simulated camera resetting...")

    def close(self):
        """
        Close the camera.
        """

        pass

    def grab_frame(self) -> NDArray[np.int_]:
        """
        Grab a frame from the camera buffer. \n
        If binning is via software, the GPU binned \n
        image is computed and returned.

        :return: The camera frame of size (height, width).
        :rtype: np.array
        """

        while not self.buffer:
            time.sleep(0.01)
        image = self.buffer.pop(0)
        if self._binning > 1:
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

        state = {
            "Frame Index": self.frame,
            "Input Buffer Size": len(self.buffer),
            "Output Buffer Size": BUFFER_SIZE_FRAMES - len(self.buffer),
            "Dropped Frames": self.dropped_frames,
            "Data Rate [MB/s]": (
                    self.frame_rate
                    * self._width_px
                    * self._height_px
                    * np.dtype(self._pixel_type).itemsize
                    / self._binning ** 2
                    / 1e6
            ),
            "Frame Rate [fps]": self.frame_rate,
        }
        # number of underrun, i.e. dropped frames
        self.log.info(
            f"id: {self.id}, "
            f"frame: {state['Frame Index']}, "
            f"input: {state['Input Buffer Size']}, "
            f"output: {state['Output Buffer Size']}, "
            f"dropped: {state['Dropped Frames']}, "
            f"data rate: {state['Data Rate [MB/s]']:.2f} [MB/s], "
            f"frame rate: {state['Frame Rate [fps]']:.2f} [fps]."
        )
        return state

    def log_metadata(self):
        """Log all metadata from the camera to the logger."""

        pass

    def _generate_frames(self, frame_count: int):
        """
        Internal function that generates simulated camera frames.

        :param frame_count: The number of frames to generate
        :type frame_count: int
        """

        self.frame = 0
        self.frame_rate = 0
        self.dropped_frames = 0
        i = 1
        frame_count = frame_count if frame_count is not None else 1
        while i <= frame_count and not self.terminate_frame_grab.is_set():
            start_time = time.time()
            column_count = self._width_px
            row_count = self._height_px
            image = np.random.randint(
                low=128,
                high=256,
                size=(row_count, column_count),
                dtype=np.dtype(PIXEL_TYPES[self._pixel_type]),
            )
            while (time.time() - start_time) < self.frame_time_ms / 1000:
                time.sleep(0.01)
            self.buffer.append(image)
            self.frame += 1
            i = i if frame_count is None else i + 1
            end_time = time.time()
            self.frame_rate = 1 / (end_time - start_time)


# Example usage
if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    camera = SimulatedCamera(id="main-camera", serial_number="sim-cam-001")
    camera.binning = 2
    camera.roi_width_px = 14170
    camera.roi_height_px = 10624
    camera.binning = 4
    camera.prepare()
    camera.start(10)
    for i in range(10):
        frame = camera.grab_frame()
        print(frame)
    camera.stop()
    camera.close()
    print("done")
