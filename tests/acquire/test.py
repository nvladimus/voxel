from voxel.devices.camera.vieworks_acquire import Camera
from voxel.writers.acquire_zarr import AcquireZarrWriter
import time
import os
import logging
import sys
from logging import FileHandler

os.environ["ZARR_V3_EXPERIMENTAL_API"] = "1"
os.environ["ZARR_V3_SHARDING"] = "1"

if __name__ == '__main__':

    logger = logging.getLogger()
    logging.getLogger().handlers.clear()
    logger.setLevel(logging.DEBUG)
    fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s'
    datefmt = '%Y-%m-%d,%H:%M:%S'
    log_formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    file_handler = FileHandler('D:\\output.log', 'w')
    file_handler.setLevel('DEBUG')
    file_handler.setFormatter(log_formatter)
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel('DEBUG')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(log_handler)

    max_frame_count = 128

    camera = Camera(id='MP151BBX006')
    camera.exposure_time_ms = 10.0
    camera.width_px = 14192
    camera.height_px = 10640
    camera.trigger = {
        "mode": "off",
        "source": "line0",
        "polarity": "risingedge"
    }
    camera.pixel_type = 'mono16'
    camera.binning = 1

    # note data will be saved to
    # path \\ acquistion_name \\ filename.zarr
    writer = AcquireZarrWriter(path="D:\\")
    writer.frame_count_px = max_frame_count
    writer.column_count_px = 14192
    writer.row_count_px = 10640
    writer.chunk_size_x_px = 128
    writer.chunk_size_y_px = 128
    writer.chunk_size_z_px = 32
    writer.shard_size_x_chunks = 111
    writer.shard_size_y_chunks = 84
    writer.shard_size_z_chunks = 1
    writer.x_voxel_size_um = 1
    writer.y_voxel_size_um = 1
    writer.compression = 'zstdshuffle'
    writer.acquisition_name = 'test'
    writer.filename = 'data'
    writer.prepare()

    camera.start(frame_count=max_frame_count)

    frames_collected = 0
    while frames_collected < writer.frame_count_px-1:
        with camera.runtime.get_available_data(0) as data:
            packet = data.get_frame_count()
            frames_collected += packet
            if packet != 0:
                logger.info(f"id: {camera.id}, frame: {frames_collected}")

    camera.stop()
    camera.close()

    # temporary -- runtime will segfault without this
    time.sleep(1)

    log_handler.close()
    logger.removeHandler(log_handler)