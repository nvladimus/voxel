import queue
import time
from threading import Thread, Lock, Event
from typing import Any, Tuple

import numpy as np
from numpy.typing import NDArray

from voxel.descriptors.deliminated_property import DeliminatedProperty
from voxel.devices.camera.base import BaseCamera
from voxel.devices.camera.codes import (
    TriggerMode, TriggerPolarity, TriggerSource, TriggerSettings, TriggerLUT, PixelType, PixelTypeLUT,
    BinningLUT, Binning, BitPackingModeLUT, BitPackingMode, PixelTypeInfo, AcquisitionState
)
from voxel.devices.utils.geometry import Vec2D
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


class SimulatedCameraInstance:
    line_interval_us_lut = {np.uint8: 10.00, np.uint16: 20.00}

    def __init__(self):
        self.sensor_width_px: int = MAX_WIDTH_PX
        self.sensor_height_px: int = MAX_HEIGHT_PX
        self.roi_width_px: int = MAX_WIDTH_PX
        self.roi_height_px: int = MAX_HEIGHT_PX
        self.roi_step_width_px: int = STEP_WIDTH_PX
        self.roi_step_height_px: int = STEP_HEIGHT_PX
        self.roi_width_offset_px: int = 0
        self.roi_height_offset_px: int = 0
        self.binning: int = 1
        self.pixel_type: Any = np.uint16
        self.bit_packing_mode: str = "lsb"
        self.min_exposure_time_ms: float = MIN_EXPOSURE_TIME_MS
        self.max_exposure_time_ms: float = MAX_EXPOSURE_TIME_MS
        self.step_exposure_time_ms: float = STEP_EXPOSURE_TIME_MS
        self.exposure_time_ms: float = MIN_EXPOSURE_TIME_MS * 1e2
        self.readout_mode: str = "default"
        self.trigger_mode: str = "On"
        self.trigger_source: str = "None"
        self.trigger_activation: str = "RisingEdge"

        self.is_running: bool = False
        self.frame_buffer = queue.Queue(maxsize=BUFFER_SIZE_FRAMES)
        self.queue_lock = Lock()
        self.generation_thread = None
        self.stop_event = Event()
        self.frame_rate = 0.0
        self.dropped_frames = 0
        self.frame_count = 0
        self.start_time = None

    def start_acquisition(self, frame_count: int = -1):
        if self.is_running:
            return
        self.frame_rate = 0.0
        self.dropped_frames = 0
        self.frame_count = 0
        self.start_time = None
        self.is_running = True
        self.stop_event.clear()
        self.generation_thread = Thread(
            target=self._generate_frames_thread,
            args=(frame_count,)
        )
        self.generation_thread.start()

    def _generate_frames_thread(self, frame_count: int = -1):
        frame_time_ms = ((self.line_interval_us_lut[self.pixel_type] * self.roi_height_px / 1000)
                         + self.exposure_time_ms)
        frame_time_s = frame_time_ms / 1000
        frame_shape = (self.roi_height_px, self.roi_width_px)
        frames_generated = 0
        self.start_time = time.perf_counter()

        while self.is_running and (frame_count == -1 or frames_generated < frame_count):
            frame_start_time = time.perf_counter()

            # Generate frame with a timestamp and frame count
            frame = np.random.randint(128, 256, size=frame_shape, dtype=self.pixel_type)
            timestamp = time.time()
            self.frame_count += 1
            frame_with_metadata = (frame, timestamp, self.frame_count)

            with self.queue_lock:
                if self.frame_buffer.full():
                    try:
                        self.frame_buffer.get_nowait()
                        self.dropped_frames += 1
                    except queue.Empty:
                        pass
                self.frame_buffer.put(frame_with_metadata)

            frames_generated += 1

            # Calculate time to sleep
            elapsed_time = time.perf_counter() - frame_start_time
            sleep_time = frame_time_s - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

            self.frame_rate = frames_generated / (time.perf_counter() - self.start_time)

            if self.stop_event.is_set():
                break

    def grab_frame(self) -> Tuple[NDArray[np.int_], float, int]:
        """Grab a frame from the queue."""
        try:
            with self.queue_lock:
                return self.frame_buffer.get_nowait()
        except queue.Empty:
            return np.zeros((self.roi_height_px, self.roi_width_px), dtype=self.pixel_type), time.time(), 0

    def stop_acquisition(self):
        """Stop frame acquisition."""
        self.is_running = False
        self.stop_event.set()
        if self.generation_thread:
            self.generation_thread.join()
        self.generation_thread = None

    def close(self):
        """Clean up resources."""
        self.stop_acquisition()


class SimulatedCamera(BaseCamera):

    def __init__(self, id: str, serial_number: str):
        super().__init__(id)
        self.serial_number = serial_number
        self.instance = SimulatedCameraInstance()

        # Property LUTs
        self.trigger_lut = TriggerLUT
        self.pixel_type_lut: PixelTypeLUT
        self.binning_lut: BinningLUT
        self.bit_packing_lut: BitPackingModeLUT

        self._generate_luts()

        # cache properties
        self._trigger_cache = None
        self._pixel_type_cache = None
        self._binning_cache = None
        self._bit_packing_mode_cache = None

        self.gpu_binning = DownSample2D(binning=self.binning)

        self.log.debug(f"simulated camera initialized with id: {id}, serial number: {serial_number}")
        self.log.debug(f"   simulated camera instance: {self.instance}")

    def _generate_luts(self):
        self.trigger_lut = TriggerLUT(
            mode={TriggerMode.ON: "On", TriggerMode.OFF: "Off"},
            source={TriggerSource.INTERNAL: "None", TriggerSource.EXTERNAL: "Line0"},
            polarity={TriggerPolarity.RISING: "RisingEdge", TriggerPolarity.FALLING: "FallingEdge"},
        )
        self.pixel_type_lut: PixelTypeLUT = {
            PixelType.MONO8: PixelTypeInfo(np.uint8, self.instance.line_interval_us_lut[np.uint8]),
            PixelType.MONO16: PixelTypeInfo(np.uint16, self.instance.line_interval_us_lut[np.uint16]),
        }
        self.binning_lut: BinningLUT = {
            1: 1,
            2: 2,
            4: 4
        }
        self.bit_packing_lut: BitPackingModeLUT = {
            BitPackingMode.LSB: "lsb",
            BitPackingMode.MSB: "msb",
            BitPackingMode.NONE: "none"
        }

    # TODO: Update DeliminatedProperty to use callables
    @DeliminatedProperty(
        minimum=MIN_WIDTH_PX,
        maximum=MAX_WIDTH_PX,
        step=STEP_WIDTH_PX, unit="px"
    )
    def roi_width_px(self) -> int:
        return self.instance.roi_width_px

    @roi_width_px.setter
    def roi_width_px(self, value: int) -> None:
        self.instance.roi_width_px = value
        centered_offset_px = (
                round((self.instance.sensor_width_px / 2 - value / 2) / self.instance.roi_step_width_px)
                * self.instance.roi_step_width_px
        )
        self.instance.roi_width_offset_px = centered_offset_px
        self.log.debug(f'ROI width set to: {value} px')

    @property
    def roi_width_offset_px(self) -> int:
        return self.instance.roi_width_offset_px

    @property
    def sensor_width_px(self) -> int:
        return self.instance.sensor_width_px

    @DeliminatedProperty(
        minimum=MIN_HEIGHT_PX,
        maximum=MAX_HEIGHT_PX,
        step=STEP_HEIGHT_PX, unit="px"
    )
    def roi_height_px(self) -> int:
        return self.instance.roi_height_px

    @roi_height_px.setter
    def roi_height_px(self, value: int) -> None:
        self.instance.roi_height_px = value
        centered_offset_px = (
                round((self.instance.sensor_height_px / 2 - value / 2) / self.instance.roi_step_height_px)
                * self.instance.roi_step_height_px
        )
        self.instance.roi_height_offset_px = centered_offset_px
        self.log.debug(f'ROI height set to: {value} px')

    @property
    def roi_height_offset_px(self) -> int:
        return self.instance.roi_height_offset_px

    @property
    def sensor_height_px(self) -> int:
        return self.instance.sensor_height_px

    @property
    def binning(self) -> Binning:
        self._binning_cache = self._get_binning()
        return self._binning_cache

    def _get_binning(self) -> Binning:
        try:
            return next(key for key, value in self.binning_lut.items() if value == self.instance.binning)
        except KeyError:
            self.log.error(f"Invalid binning from  device: {self.instance.binning}")
            return 1

    @binning.setter
    def binning(self, value: Binning) -> None:
        try:
            self.instance.binning = self.binning_lut[value]
            self.gpu_binning = DownSample2D(binning=self.binning)
        except KeyError as e:
            self.log.error(f"Invalid binning: {e}")
            return

        self.log.debug(f"Binning set to: {value}")

        # Invalidate the cached property
        self._binning_cache = None

    @property
    def image_size_px(self) -> Vec2D:
        return Vec2D(self.instance.roi_width_px, self.instance.roi_height_px) // self.binning

    @property
    def pixel_type(self) -> PixelType:
        self._pixel_type_cache = self._get_pixel_type()
        return self._pixel_type_cache

    def _get_pixel_type(self) -> PixelType:
        try:
            return next(key for key, value in self.pixel_type_lut.items() if value.repr == self.instance.pixel_type)
        except KeyError:
            self.log.error(f"Invalid pixel type: {self.instance.pixel_type}")
            return PixelType.MONO16

    @pixel_type.setter
    def pixel_type(self, pixel_type: PixelType) -> None:
        try:
            self.instance.pixel_type = self.pixel_type_lut[pixel_type]
        except KeyError as e:
            self.log.error(f"Invalid pixel type: {e}")
            return

        self.log.debug(f"Pixel type set to: {pixel_type.name}")

        # Invalidate the cached property
        self._pixel_type_cache = None

    @property
    def bit_packing_mode(self) -> BitPackingMode:
        self._bit_packing_mode_cache = self._get_bit_packing_mode()
        return self._bit_packing_mode_cache

    def _get_bit_packing_mode(self) -> BitPackingMode:
        try:
            return next(key for key, value in self.bit_packing_lut.items() if value == self.instance.bit_packing_mode)
        except KeyError:
            self.log.error(f"Invalid bit packing mode: {self.instance.bit_packing_mode}")
            return BitPackingMode.NONE

    @bit_packing_mode.setter
    def bit_packing_mode(self, bit_packing_mode: BitPackingMode) -> None:
        try:
            self.instance.bit_packing_mode = self.bit_packing_lut[bit_packing_mode]
        except KeyError as e:
            self.log.error(f"Invalid bit packing mode: {e}")
            return

        self.log.debug(f"Bit packing mode set to: {bit_packing_mode.name}")

        # Invalidate the cached property
        self._bit_packing_mode_cache = None

    @DeliminatedProperty(
        minimum=MIN_EXPOSURE_TIME_MS,
        maximum=MAX_EXPOSURE_TIME_MS,
        step=STEP_EXPOSURE_TIME_MS, unit="ms"
    )
    def exposure_time_ms(self) -> float:
        return self.instance.exposure_time_ms

    @exposure_time_ms.setter
    def exposure_time_ms(self, value: float) -> None:
        self.instance.exposure_time_ms = value
        self.log.debug(f'Exposure time set to: {value} ms')

    @property
    def line_interval_us(self) -> float:
        return self.pixel_type_lut[self.pixel_type].line_interval_us

    @property
    def frame_time_ms(self) -> float:
        return (self.line_interval_us * self.roi_height_px) / 1000 + self.exposure_time_ms

    @property
    def trigger(self) -> TriggerSettings:
        self._trigger_cache = self._get_trigger_mode()
        return self._trigger_cache

    @trigger.setter
    def trigger(self, trigger: TriggerSettings) -> None:
        try:
            self.instance.trigger_mode = self.trigger_lut.mode[trigger.mode]
            self.instance.trigger_source = self.trigger_lut.source[trigger.source]
            self.instance.trigger_activation = self.trigger_lut.polarity[trigger.polarity]
        except KeyError as e:
            self.log.error(f"Invalid trigger setting: {e}")
            return

        self.log.debug(f"Trigger set to: mode={trigger.mode.name}, "
                       f"source={trigger.source.name}, polarity={trigger.polarity.name}")

        # Invalidate the cached property
        self._trigger_cache = None

    def _get_trigger_mode(self):
        try:
            return TriggerSettings(
                mode=next(
                    key for key, value in self.trigger_lut.mode.items() if value == self.instance.trigger_mode),
                source=next(
                    key for key, value in self.trigger_lut.source.items() if value == self.instance.trigger_source),
                polarity=next(key for key, value in self.trigger_lut.polarity.items() if
                              value == self.instance.trigger_activation)
            )
        except StopIteration:
            self.log.error(f"Invalid trigger settings recieved from camera: mode={self.instance.trigger_mode}, "
                           f"source={self.instance.trigger_source}, activation={self.instance.trigger_activation}")
            return TriggerSettings(TriggerMode.OFF, TriggerSource.INTERNAL, TriggerPolarity.RISING)

    def prepare(self) -> None:
        pass

    def start(self, frame_count: int) -> None:
        self.instance.start_acquisition(frame_count)

    def stop(self) -> None:
        self.instance.stop_acquisition()

    def reset(self) -> None:
        self.stop()
        self._generate_luts()
        self._binning_cache = None
        self._pixel_type_cache = None
        self._bit_packing_mode_cache = None
        self._trigger_cache = None
        self.trigger = TriggerSettings(TriggerMode.OFF, TriggerSource.INTERNAL, TriggerPolarity.RISING)

    def grab_frame(self) -> NDArray[np.int_]:
        frame, timestamp, frame_count = self.instance.grab_frame()
        return frame if self.binning == 1 else self.gpu_binning.run(frame)

    @property
    def acquisition_state(self) -> AcquisitionState:
        return AcquisitionState(
            frame_index=self.instance.frame_count,
            input_buffer_size=self.instance.frame_buffer.qsize(),
            output_buffer_size=self.instance.frame_buffer.qsize(),
            dropped_frames=self.instance.dropped_frames,
            data_rate_mbs=self.instance.frame_rate * self.roi_width_px * self.roi_height_px * (
                16 if self.pixel_type == PixelType.MONO16 else 8) / 8 / 1e6,
            frame_rate_fps=self.instance.frame_rate
        )

    def log_metadata(self) -> None:
        pass

    def close(self):
        self.instance.close()


# Example usage
if __name__ == "__main__":
    camera = SimulatedCamera(id="main-camera", serial_number="sim-cam-001")

    num_frames = 15
    print(f'\nStarting acquisition of {num_frames} frames')

    frame_time_s = camera.frame_time_ms / 1000
    wait_time = frame_time_s * 1.5  # Add 25% buffer
    print(f'Frame time:{frame_time_s}, Wait_time: {wait_time!s}')

    camera.start(-1)

    # Wait for the first frame to be generated
    time.sleep(frame_time_s * 2)
    print(len(camera.instance.frame_buffer.queue))

    sample_frames = []
    dropped_frames = []
    frame_rates = []
    empty_frames = 0

    for i in range(num_frames):
        frame = camera.grab_frame()
        sample_frames.append(frame[:1, :5])
        frame_rate = camera.acquisition_state.frame_rate_fps
        wait_time = 1 / frame_rate * 1.1
        frame_rates.append(camera.acquisition_state.frame_rate_fps)
        dropped_frames.append(camera.acquisition_state.dropped_frames)
        if frame[0, 0] == 0:
            empty_frames += 1

        time.sleep(wait_time)

    camera.stop()

    for i, frame in enumerate(sample_frames):
        print(f'frame {i}:  {frame}, dropped frames: {dropped_frames[i]}, frame_time: {1 / frame_rates[i]}')

    print(f'Empty frames: {empty_frames}')
    print(f'Dropped frames: {camera.acquisition_state.dropped_frames}')

    camera.close()
    print("done")
