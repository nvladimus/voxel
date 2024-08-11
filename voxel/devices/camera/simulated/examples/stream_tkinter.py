import tkinter as tk
from PIL import Image, ImageTk
import time
from typing import Optional
import numpy as np
from voxel.devices.camera.simulated.simulated_camera import SimulatedCamera


class FrameStreamApp(tk.Tk):
    def __init__(self, camera: SimulatedCamera, duration: Optional[float] = None):
        super().__init__()

        self.camera = camera
        self.duration = duration
        self.start_time = time.time()
        self.last_frame_time = self.start_time
        self.frames_processed = 0

        self.title("Frame Stream")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, width=800, height=500)
        self.canvas.pack()

        self.info_label = tk.Label(self, text="", justify=tk.LEFT)
        self.info_label.pack(pady=10)

        self.image_on_canvas = None

        self.camera.stop()
        self.camera.start(-1)  # Start continuous acquisition

        self.update_frame()

    def update_frame(self):
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        if self.duration and elapsed_time >= self.duration:
            self.quit()
            return

        state = self.camera.acquisition_state
        expected_frames = int(state.frame_rate_fps * elapsed_time)
        frames_to_process = max(0, expected_frames - self.frames_processed)

        for _ in range(frames_to_process):
            frame = self.camera.grab_frame()
            self.frames_processed += 1

            # Only display the last frame if we processed multiple
            if _ == frames_to_process - 1:
                # Normalize the frame to 0-255 range for display
                frame_normalized = ((frame - frame.min()) * (255.0 / (frame.max() - frame.min()))).astype(np.uint8)

                image = Image.fromarray(frame_normalized)
                photo = ImageTk.PhotoImage(image=image)

                # Update canvas
                if self.image_on_canvas is None:
                    self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                else:
                    self.canvas.itemconfig(self.image_on_canvas, image=photo)

                self.canvas.image = photo  # Keep a reference to prevent garbage collection

        actual_fps = self.frames_processed / elapsed_time if elapsed_time > 0 else 0
        info_text = (f"Camera Frame Rate: {state.frame_rate_fps:.2f} fps\n"
                     f"Actual Frame Rate: {actual_fps:.2f} fps\n"
                     f"Frame Index: {state.frame_index}\n"
                     f"Processed Frames: {self.frames_processed}\n"
                     f"Dropped Frames: {state.dropped_frames}\n"
                     f"Data Rate: {state.data_rate_mbs:.2f} MB/s\n"
                     f"Elapsed Time: {elapsed_time:.2f} s")
        self.info_label.config(text=info_text)

        print(f"\rCamera FPS: {state.frame_rate_fps:.2f}, Actual FPS: {actual_fps:.2f}, "
              f"Processed Frames: {self.frames_processed}, Elapsed Time: {elapsed_time:.2f} s", end="")

        self.after(1, self.update_frame)  # Schedule the next update

    def on_closing(self):
        self.camera.stop()
        self.quit()


def stream_frames_tkinter(camera: SimulatedCamera, duration: Optional[float] = None):
    app = FrameStreamApp(camera, duration)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    print("\nStreaming stopped.")


# Example usage
if __name__ == "__main__":
    simulated_camera = SimulatedCamera(id="main-camera", serial_number="sim-cam-001")
    simulated_camera.roi_height_px //= 2
    simulated_camera.roi_width_px //= 2
    simulated_camera.exposure_time_ms = 1  # Set exposure time to 10 ms

    print("Starting frame streaming.")
    try:
        stream_frames_tkinter(simulated_camera, duration=1*60)  # Stream for 30 seconds
    except KeyboardInterrupt:
        print("\nStreaming interrupted by user.")
    finally:
        simulated_camera.close()
    print("Done")
