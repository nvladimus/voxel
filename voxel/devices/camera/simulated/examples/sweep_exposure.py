import time
from typing import Tuple, List, Sequence

import numpy as np

from voxel.devices.camera.base import VoxelCamera
from voxel.devices.camera.codes import VoxelFrame
from voxel.devices.camera.simulated.simulated_camera import SimulatedCamera


def grab_x_frames(camera: VoxelCamera, num_frames: int) -> Tuple[List[VoxelFrame], int, int, float]:
    camera.log.debug(f"Grabbing {num_frames} frames")
    camera.stop()
    camera.start(num_frames)
    collected_frames = []
    empty = 0
    wait_time = (camera.frame_time_ms / 1000) * 1.1
    time.sleep(wait_time * 2)
    for _ in range(num_frames):
        frame = camera.grab_frame()
        if frame[0, 0] == 0:
            empty += 1
        if camera.acquisition_state.dropped_frames > 0:
            wait_time = 1 / camera.acquisition_state.frame_rate_fps * 1.1
        time.sleep(wait_time)
        collected_frames.append(frame)

    camera.stop()
    return collected_frames, empty, camera.acquisition_state.dropped_frames, camera.acquisition_state.frame_rate_fps


def plot_exposure_times_vs_frame_rate(exposure_times: Sequence, frame_rates: List[float], title: str):
    """
    Plot exposure times vs frame rates.
    :param exposure_times: List of exposure times in ms.
    :param frame_rates: List of frame rates in fps.
    :param title: Title of the plot.
    """
    plt.figure(figsize=(12, 8))
    plt.semilogx(exposure_times, frame_rates, marker='o', linestyle='-', markersize=4)
    plt.xlabel('Exposure Time (ms)')
    plt.ylabel('Frame Rate (fps)')
    plt.title(title)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlim(MIN_EXPOSURE_TIME_MS, MAX_EXPOSURE_TIME_MS)

    # Format x-axis labels
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}' if x >= 1 else f'{x:.1e}'))

    # Add some value annotations (not all to avoid clutter)
    for i in range(0, len(exposure_times), len(exposure_times) // 10):
        plt.annotate(f'{frame_rates[i]:.2f}', (exposure_times[i], frame_rates[i]),
                     textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8)

    plt.tight_layout()
    file_name = title.replace(" ", "_").lower()
    plt.savefig(f'{file_name}.png', dpi=300)
    plt.show()


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    MIN_EXPOSURE_TIME_MS = 0.001
    MAX_EXPOSURE_TIME_MS = 6e2

    simulated_camera = SimulatedCamera(id="main-camera", serial_number="sim-cam-001")
    simulated_camera.roi_height_px //= 4
    simulated_camera.roi_width_px //= 4

    # Generate logarithmically spaced exposure times
    num_points = 10
    num_frames = 20

    exposure_times = np.logspace(np.log10(MIN_EXPOSURE_TIME_MS), np.log10(MAX_EXPOSURE_TIME_MS), num_points)

    frame_rates = []
    empty_frames = []
    dropped_frames = []

    for exposure_time in exposure_times:
        print(f"Measuring frame rate for exposure time: {exposure_time:.3f} ms")
        simulated_camera.exposure_time_ms = exposure_time
        frames, empty, dropped, frame_rate = grab_x_frames(simulated_camera, num_frames)
        frame_rates.append(frame_rate)
        dropped_frames.append(dropped)
        empty_frames.append(empty)
        print(f"Frame rate: {frame_rate:.2f} fps,  Empty frames: {empty}, Dropped frames: {dropped}")
        # print("Empty frames: ", empty_frames)
        # print("Dropped frames: ", dropped_frames)
        print()

    simulated_camera.close()

    plot_exposure_times_vs_frame_rate(exposure_times, frame_rates, "Exposure Time vs Frame Rate")
    print("Done")