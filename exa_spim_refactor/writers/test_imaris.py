import numpy
import time
import math
import threading
from pathlib import Path
from spim_core.config_base import Config
from threading import Event, Thread
from data_structures.shared_double_buffer import SharedDoubleBuffer
from multiprocessing.shared_memory import SharedMemory
from imaris import Writer

if __name__ == '__main__':

    this_dir = Path(__file__).parent.resolve() # directory of this test file.
    config_path = this_dir / Path("test_imaris.yaml")
    config = Config(str(config_path))

    chunk_size_frames = 64
    num_frames = 256
    num_tiles = 1

    stack_writer_worker = Writer()
    stack_writer_worker.row_count_px = 2048
    stack_writer_worker.column_count_px = 2048
    stack_writer_worker.x_voxel_size_um = 0.748
    stack_writer_worker.y_voxel_size_um = 0.748
    stack_writer_worker.z_voxel_size_um = 1
    stack_writer_worker.theta_deg = 45
    stack_writer_worker.frame_count_px = num_frames
    stack_writer_worker.compression = config.cfg['writer']['compression']
    stack_writer_worker.data_type = config.cfg['writer']['data_type']
    stack_writer_worker.path = config.cfg['writer']['path']
    stack_writer_worker.color = config.cfg['writer']['color']
    stack_writer_worker.channel = '488'
    frame_index = 0
    tile_index = 0

    for tile_index in range(num_tiles):

        # update filename
        stack_writer_worker.filename = f'test_{tile_index}.ims'
        
        # move tile over 1 mm
        stack_writer_worker.x_position_mm = 0 + tile_index*1.000
        stack_writer_worker.y_position_mm = 0
        stack_writer_worker.z_position_mm = 0
        stack_writer_worker.prepare()
        stack_writer_worker.start()

        chunk_count = math.ceil(num_frames / chunk_size_frames)
        remainder = num_frames % chunk_size_frames
        last_chunk_size = chunk_size_frames if not remainder else remainder
        last_frame_index = num_frames - 1

        mem_shape = (chunk_size_frames,
                     stack_writer_worker.row_count_px,
                     stack_writer_worker.column_count_px)

        img_buffer = SharedDoubleBuffer(mem_shape,
                                        dtype=config.cfg['writer']['data_type'])

        chunk_lock = threading.Lock()

        # Images arrive serialized in repeating channel order.
        for stack_index in range(num_frames):
            chunk_index = stack_index % chunk_size_frames
            # Start a batch of pulses to generate more frames and movements.
            img_buffer.get_last_image()
            if chunk_index == 0:
                chunks_filled = math.floor(stack_index / chunk_size_frames)
                remaining_chunks = chunk_count - chunks_filled
            # Grab simulated frame
            if chunks_filled % 2 == 0:
                img_buffer.add_image( \
                numpy.random.randint(
                    low=0,
                    high=256,
                    size=(stack_writer_worker.row_count_px, stack_writer_worker.column_count_px),
                    dtype = config.cfg['writer']['data_type']
                ))
            else:
                img_buffer.add_image( \
                    numpy.random.randint(
                        low=0,
                        high=32,
                        size=(stack_writer_worker.row_count_px, stack_writer_worker.column_count_px),
                        dtype = config.cfg['writer']['data_type']
                    ))

            # mimic 5 fps imaging
            time.sleep(0.05)
            frame_index += 1
            # Dispatch either a full chunk of frames or the last chunk,
            # which may not be a multiple of the chunk size.
            if chunk_index == chunk_size_frames - 1 or stack_index == last_frame_index:
                while not stack_writer_worker.done_reading.is_set():
                    time.sleep(0.001)
                # Dispatch chunk to each StackWriter compression process.
                # Toggle double buffer to continue writing images.
                # To read the new data, the StackWriter needs the name of
                # the current read memory location and a trigger to start.
                # Lock out the buffer before toggling it such that we
                # don't provide an image from a place that hasn't been
                # written yet.
                with chunk_lock:
                    img_buffer.toggle_buffers()
                    if config.cfg['writer']['path'] is not None:
                        stack_writer_worker.shm_name = \
                            img_buffer.read_buf_mem_name
                        stack_writer_worker.done_reading.clear()

        stack_writer_worker.wait_to_finish()

# import numpy
# import time
# import math
# import threading
# from pathlib import Path
# from spim_core.config_base import Config
# from threading import Event, Thread
# from data_structures.shared_double_buffer import SharedDoubleBuffer
# from multiprocessing.shared_memory import SharedMemory
# from imaris import Writer

# if __name__ == '__main__':

#     this_dir = Path(__file__).parent.resolve() # directory of this test file.
#     config_path = this_dir / Path("test_imaris.yaml")
#     config = Config(str(config_path))

#     stack_writer_worker = Writer()
#     stack_writer_worker.row_count_px = 10640
#     stack_writer_worker.column_count_px = 14192
#     stack_writer_worker.frame_count_px = 128
#     stack_writer_worker.x_position_mm = 0
#     stack_writer_worker.y_position_mm = 0
#     stack_writer_worker.z_position_mm = 0
#     stack_writer_worker.x_voxel_size_um = 0.748
#     stack_writer_worker.y_voxel_size_um = 0.748
#     stack_writer_worker.z_voxel_size_um = 1
#     stack_writer_worker.compression = config.cfg['writer']['compression']
#     stack_writer_worker.data_type = config.cfg['writer']['data_type']
#     stack_writer_worker.path = config.cfg['writer']['path']
#     stack_writer_worker.filename = 'test.ims'
#     stack_writer_worker.channel = '488'
#     stack_writer_worker.color = config.cfg['writer']['hex_color']
#     stack_writer_worker.prepare()
#     stack_writer_worker.start()

#     chunk_lock = threading.Lock()

#     mem_shape = (64,
#                  14192,
#                  10640)

#     img_buffer = SharedDoubleBuffer(mem_shape,
#                                     dtype=config.cfg['writer']['data_type'])

#     frame_index = 0
#     chunk_count = math.ceil(128 / 64)
#     remainder = 128 % 64
#     last_chunk_size = 64 if not remainder else remainder
#     last_frame_index = 128 - 1

#     # Images arrive serialized in repeating channel order.
#     for stack_index in range(128):
#         print(stack_index)
#         chunk_index = stack_index % 64
#         # Start a batch of pulses to generate more frames and movements.
#         if chunk_index == 0:
#             chunks_filled = math.floor(stack_index / 64)
#             remaining_chunks = chunk_count - chunks_filled
#         # Gran simulated frame
#         img_buffer.write_buf[chunk_index] = \
#             numpy.random.randint(low=0, high=1, size=(14192, 10640), dtype = config.cfg['writer']['data_type'])
#         # mimic 5 fps imaging
#         time.sleep(0.2)

#         frame_index += 1
#         # Dispatch either a full chunk of frames or the last chunk,
#         # which may not be a multiple of the chunk size.
#         if chunk_index == 64 - 1 or stack_index == last_frame_index:
#             while not stack_writer_worker.done_reading.is_set():
#                 time.sleep(0.001)
#             # Dispatch chunk to each StackWriter compression process.
#             # Toggle double buffer to continue writing images.
#             # To read the new data, the StackWriter needs the name of
#             # the current read memory location and a trigger to start.
#             # Lock out the buffer before toggling it such that we
#             # don't provide an image from a place that hasn't been
#             # written yet.
#             with chunk_lock:
#                 img_buffer.toggle_buffers()
#                 if config.cfg['writer']['path'] is not None:
#                     stack_writer_worker.shm_name = \
#                         img_buffer.read_buf_mem_name
#                     stack_writer_worker.done_reading.clear()

#     stack_writer_worker.wait_to_finish()