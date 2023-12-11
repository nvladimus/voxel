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

	stack_writer_worker = Writer()
	stack_writer_worker.row_count = 14192
	stack_writer_worker.column_count = 10640
	stack_writer_worker.frame_count = 128
	stack_writer_worker.chunk_count = 64
	stack_writer_worker.x_pos = 0
	stack_writer_worker.y_pos = 0
	stack_writer_worker.x_voxel_size = 0.748
	stack_writer_worker.y_voxel_size = 0.748
	stack_writer_worker.z_voxel_size = 1
	stack_writer_worker.compression = config.cfg['writer']['compression']
	stack_writer_worker.dtype = config.cfg['writer']['data_type']
	stack_writer_worker.path = config.cfg['writer']['path']
	stack_writer_worker.filename = 'test.ims'
	stack_writer_worker.channel = '488'
	stack_writer_worker.color = config.cfg['writer']['hex_color']
	stack_writer_worker.buffer()
	stack_writer_worker.start()

	chunk_lock = threading.Lock()

	mem_shape = (64,
	             14192,
	             10640)

	img_buffer = SharedDoubleBuffer(mem_shape,
	                                dtype=config.cfg['writer']['data_type'])

	frame_index = 0
	chunk_count = math.ceil(128 / 64)
	remainder = 128 % 64
	last_chunk_size = 64 if not remainder else remainder
	last_frame_index = 128 - 1

	# Images arrive serialized in repeating channel order.
	for stack_index in range(128):
	    chunk_index = stack_index % 64
	    # Start a batch of pulses to generate more frames and movements.
	    if chunk_index == 0:
	        chunks_filled = math.floor(stack_index / 64)
	        remaining_chunks = chunk_count - chunks_filled
	    # Gran simulated frame
	    img_buffer.write_buf[chunk_index] = \
	    	numpy.random.randint(low=0, high=1, size=(14192, 10640), dtype = config.cfg['writer']['data_type'])
	    # mimic 5 fps imaging
	    time.sleep(0.2)

	    frame_index += 1
	    # Dispatch either a full chunk of frames or the last chunk,
	    # which may not be a multiple of the chunk size.
	    if chunk_index == 64 - 1 or stack_index == last_frame_index:
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
	stack_writer_worker.close()