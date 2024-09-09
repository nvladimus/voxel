import queue
import time
from threading import Thread, Lock, Event
from typing import Tuple, Optional

import numpy as np
from numpy.typing import NDArray

from voxel.instrument.devices.camera import ROI
from voxel.instrument.devices.camera.simulated.definitions import TriggerMode, TriggerSource, TriggerPolarity, PixelType
from voxel.instrument.devices.camera.simulated.image_model import ImageModel
from voxel.utils.geometry import Vec2D

BUFFER_SIZE_FRAMES = 8
MIN_WIDTH_PX = 64
STEP_WIDTH_PX = 16
MIN_HEIGHT_PX = 2
STEP_HEIGHT_PX = 2
MIN_EXPOSURE_TIME_MS = 0.001
MAX_EXPOSURE_TIME_MS = 1e3
STEP_EXPOSURE_TIME_MS = 1
INIT_EXPOSURE_TIME_MS = 500


# Vieworks VNP-604MX
# ImageModel(
#     qe=0.85,
#     gain=0.08,
#     dark_noise=6.89,
#     bitdepth=12,
#     baseline=0
#     reference_image_path=reference_image_path,
# )

DEFAULT_IMAGE_MODEL = {
    "qe": 0.85,
    "gain": 0.08,
    "dark_noise": 6.89,
    "bitdepth": 12,
    "baseline": 0,
}

LINE_INTERVAL_US_LUT = {PixelType.MONO8: 10.00, PixelType.MONO16: 20.00}


class SimulatedCameraHardware:

    def __init__(self, image_model: Optional[ImageModel]= None, reference_image_path: Optional[str] = None):

        if image_model is None:
            image_model = ImageModel(**DEFAULT_IMAGE_MODEL, reference_image_path=reference_image_path)

        self.image_model = image_model
        self.sensor_width_px: int = self.image_model.sensor_size_px[1]
        self.sensor_height_px: int = self.image_model.sensor_size_px[0]
        self.roi_width_px: int = self.sensor_width_px
        self.roi_height_px: int = self.sensor_height_px
        self.roi_step_width_px: int = STEP_WIDTH_PX
        self.roi_step_height_px: int = STEP_HEIGHT_PX
        self.roi_width_offset_px: int = 0
        self.roi_height_offset_px: int = 0
        self.pixel_type = next(iter(PixelType))
        self.min_exposure_time_ms: float = MIN_EXPOSURE_TIME_MS
        self.max_exposure_time_ms: float = MAX_EXPOSURE_TIME_MS
        self.step_exposure_time_ms: float = STEP_EXPOSURE_TIME_MS
        self.exposure_time_ms: float = INIT_EXPOSURE_TIME_MS
        self.bit_packing_mode: str = "lsb"
        self.readout_mode: str = "default"
        self.trigger_mode: str = next(iter(TriggerMode))
        self.trigger_source: str = next(iter(TriggerSource))
        self.trigger_activation: str = next(iter(TriggerPolarity))

        self.sensor_temperature_c: float = np.random.uniform(49, 55)
        self.mainboard_temperature_c: float = np.random.uniform(25, 30)

        self.line_interval_us_lut = LINE_INTERVAL_US_LUT

        self.is_running: bool = False
        self.frame_buffer = queue.Queue(maxsize=BUFFER_SIZE_FRAMES)
        self.queue_lock = Lock()
        self.generation_thread = None
        self.stop_event = Event()
        self.frame_rate = 1 / self._calculate_frame_time_s()
        self.dropped_frames = 0
        self.frame_index = 0
        self.start_time = None

    @property
    def roi(self) -> ROI:
        return ROI(
            origin=Vec2D(self.roi_width_offset_px, self.roi_height_offset_px),
            size=Vec2D(self.roi_width_px, self.roi_height_px),
            bounds=Vec2D(self.sensor_width_px, self.sensor_height_px)
        )

    def _calculate_frame_time_s(self) -> float:
        readout_time = (self.line_interval_us_lut[self.pixel_type] * self.roi_height_px) / 1000
        frame_time_ms = self.exposure_time_ms + readout_time
        return frame_time_ms / 1000

    def start_acquisition(self, frame_count: int = -1):
        if self.is_running:
            return
        self.frame_rate = 0.0
        self.dropped_frames = 0
        self.frame_index = 0
        self.start_time = None
        self.is_running = True
        self.stop_event.clear()
        self.generation_thread = Thread(
            target=self._generate_frames_thread,
            args=(frame_count,)
        )
        self.generation_thread.start()

    def _generate_frames_thread(self, frame_count: int = -1):
        frame_time_s = self._calculate_frame_time_s()
        frames_generated = 0
        self.start_time = time.perf_counter()

        while self.is_running and (frame_count == -1 or frames_generated < frame_count):
            frame_start_time = time.perf_counter()

            # Generate frame using ImageModel
            frame = self.image_model.generate_frame(
                exposure_time=self.exposure_time_ms / 1000,
                roi = self.roi,
                pixel_type=self.pixel_type.numpy_dtype
            )
            timestamp = time.time()
            self.frame_index += 1
            frame_with_metadata = (frame, timestamp, self.frame_index)

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
            return np.zeros((self.roi_height_px, self.roi_width_px), dtype=self.pixel_type.numpy_dtype), time.time(), 0

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
