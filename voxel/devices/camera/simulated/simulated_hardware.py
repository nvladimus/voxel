import queue
import time

import numpy as np

from typing import Any, Tuple
from numpy.typing import NDArray
from threading import Thread, Lock, Event

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

LINE_INTERVAL_US_LUT = {np.uint8: 10.00, np.uint16: 20.00}


class SimulatedCameraHardware:

    def __init__(self):
        self.sensor_width_px: int = MAX_WIDTH_PX
        self.sensor_height_px: int = MAX_HEIGHT_PX
        self.roi_width_px: int = MAX_WIDTH_PX // 2
        self.roi_height_px: int = MAX_HEIGHT_PX // 2
        self.roi_step_width_px: int = STEP_WIDTH_PX
        self.roi_step_height_px: int = STEP_HEIGHT_PX
        self.roi_width_offset_px: int = MAX_WIDTH_PX // 4
        self.roi_height_offset_px: int = MAX_HEIGHT_PX // 4
        self.pixel_type: np.int_ = np.uint16
        self.bit_packing_mode: str = "lsb"
        self.min_exposure_time_ms: float = MIN_EXPOSURE_TIME_MS
        self.max_exposure_time_ms: float = MAX_EXPOSURE_TIME_MS
        self.step_exposure_time_ms: float = STEP_EXPOSURE_TIME_MS
        self.exposure_time_ms: float = MIN_EXPOSURE_TIME_MS * 1e2
        self.readout_mode: str = "default"
        self.trigger_mode: str = "On"
        self.trigger_source: str = "None"
        self.trigger_activation: str = "RisingEdge"

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

    def _calculate_frame_time_s(self) -> float:
        readout_time = (self.line_interval_us_lut[self.pixel_type] * self.roi_height_px) / 1000
        # frame_time_ms = max(self.exposure_time_ms, readout_time)
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
        frame_shape = (self.roi_height_px, self.roi_width_px)
        frames_generated = 0
        self.start_time = time.perf_counter()

        while self.is_running and (frame_count == -1 or frames_generated < frame_count):
            frame_start_time = time.perf_counter()

            # Generate frame with a timestamp and frame count
            frame = np.random.randint(0, 65535 if self.pixel_type == np.uint16 else 255,
                                      size=frame_shape, dtype=self.pixel_type)
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
