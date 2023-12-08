import numpy
import time
import math
import threading
from threading import Event, Thread
from pathlib import Path
from spim_core.config_base import Config
from data_structures.shared_double_buffer import SharedDoubleBuffer
from multiprocessing.shared_memory import SharedMemory
from imaris_writer import StackWriter

this_dir = Path(__file__).parent.resolve() # directory of this test file.
config_path = this_dir / Path("test_writer.yaml")
config = Config(str(config_path))

row_count = 128
column_count = 128
frame_count = 128
stage_x_pos_um = 0
stage_y_pos_um = 0
x_voxel_size_um = 0.748
y_voxel_size_um = 0.748
z_step_size_um = 1
chunk_size = 64
chunk_dim_order = ('z', 'y', 'x')
compressor_style = config.cfg['writer']['compression']
data_type = config.cfg['writer']['data_type']
local_storage_dir = config.cfg['writer']['path']
stack_file_name = 'test'
channel = '488'
hex_color = config.cfg['writer']['hex_color']
stack_file_name = "test.ims"

mem_shape = (chunk_size,
             row_count,
             column_count)

img_buffer = SharedDoubleBuffer(mem_shape,
                                dtype=data_type)

stack_writer_worker = \
    StackWriter(row_count,
                column_count,
                frame_count,
                stage_x_pos_um, stage_y_pos_um,
                x_voxel_size_um, y_voxel_size_um, z_step_size_um,
                chunk_size, chunk_dim_order, compressor_style,
                data_type, local_storage_dir,
                stack_file_name, channel, hex_color)

stack_writer_worker.start()

prev_frame_chunk_index = 0
frame_index = 0
chunk_count = math.ceil(frame_count / chunk_size)
remainder = frame_count % chunk_size
last_chunk_size = chunk_size if not remainder else remainder
last_frame_index = frame_count - 1
chunk_lock = threading.Lock()

# Images arrive serialized in repeating channel order.
for stack_index in range(frame_count):
    chunk_index = stack_index % chunk_size
    # Start a batch of pulses to generate more frames and movements.
    if chunk_index == 0:
        chunks_filled = math.floor(stack_index / chunk_size)
        remaining_chunks = chunk_count - chunks_filled
        # Gran simulated frame
        img_buffer.write_buf[chunk_index] = \
        numpy.random.randint(low=0, high=1, size=(row_count, column_count), dtype = data_type)
        time.sleep(0.1)
    # Save the index of the most-recently captured frame to
    # offer it to a live display upon request.
    prev_frame_chunk_index = chunk_index
    frame_index += 1
    # Dispatch either a full chunk of frames or the last chunk,
    # which may not be a multiple of the chunk size.
    if chunk_index == chunk_size - 1 or stack_index == last_frame_index:
        while not all(stack_writer_worker.done_reading.is_set()):
            time.sleep(0.001)
        # Dispatch chunk to each StackWriter compression process.
        # Toggle double buffer to continue writing images.
        # To read the new data, the StackWriter needs the name of
        # the current read memory location and a trigger to start.
        # Lock out the buffer before toggling it such that we
        # don't provide an image from a place that hasn't been
        # written yet.

        # Clear previous chunk index, so we don't provide a
        # picture that has not yet been written to this chunk.
        prev_frame_chunk_index = None
        with chunk_lock:
            img_buffer.toggle_buffers()
            if local_storage_dir is not None:
                stack_writer_worker.shm_name = \
                    img_buffer.read_buf_mem_name
                stack_writer_worker.done_reading.clear()

capture_successful = True

stack_writer_worker.close()
