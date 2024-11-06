import time
import numpy as np
import logging


def generate_frames(frame_count, frame_shape, batch_size_px, dtype, logger: logging.Logger = None):
    """Generate test frames with sequential values."""
    batch_idx = 0
    for frame_z in range(frame_count):
        start_time = time.time()
        # Fill frame with the current frame index
        frame = np.full((frame_shape.y, frame_shape.x), frame_z, dtype=dtype)
        end_time = time.time()
        time_taken = end_time - start_time
        if logger:
            logger.debug(f"Frame {frame_z} generated in {time_taken:.6f} seconds")
        # Log frame generation for debugging
        if frame_z % batch_size_px == 0:
            batch_idx += 1
        yield frame


def generate_checkered_frames(frame_count, frame_shape, dtype, logger: logging.Logger = None):
    """Generate test frames with checkerboard patterns."""
    min_tile_size = 4
    max_tile_size = min(frame_shape.x, frame_shape.y) // 4

    tile_sizes = np.linspace(min_tile_size, max_tile_size, num=frame_count, dtype=int)

    # Precompute meshgrid indices
    y_indices = np.arange(frame_shape.y)
    x_indices = np.arange(frame_shape.x)
    xv, yv = np.meshgrid(x_indices, y_indices)

    for frame_z in range(frame_count):
        start_time = time.time()
        tile_size = tile_sizes[frame_z]

        # Compute the checkerboard pattern directly
        checkerboard = ((xv // tile_size + yv // tile_size) % 2).astype(dtype)

        # Scale to full intensity range
        frame = checkerboard * 255

        end_time = time.time()
        time_taken = end_time - start_time
        if logger:
            logger.debug(f"Frame {frame_z} generated in {time_taken:.6f} seconds")

        yield frame


def generate_spiral_frames(frame_count, frame_shape, dtype, logger: logging.Logger = None):
    """Generate frames with spiral patterns."""
    min_tile_size = 2
    max_tile_size = min(frame_shape.x, frame_shape.y) // 12

    tile_sizes = np.linspace(min_tile_size, max_tile_size, num=frame_count, dtype=int)

    # Create indices centered on the frame (precomputed)
    y_indices = np.arange(frame_shape.y) - frame_shape.y // 2
    x_indices = np.arange(frame_shape.x) - frame_shape.x // 2
    xv, yv = np.meshgrid(x_indices, y_indices)

    # Precompute distance from the center
    distance = np.sqrt(xv**2 + yv**2)

    for frame_z in range(frame_count):
        start_time = time.time()
        tile_size = tile_sizes[frame_z]

        # Create expanding pattern
        pattern = ((distance // tile_size) % 2).astype(dtype)

        # Scale to full intensity range
        frame = pattern * 255

        end_time = time.time()
        time_taken = end_time - start_time
        if logger:
            logger.debug(f"Frame {frame_z} generated in {time_taken:.6f} seconds")

        yield frame
