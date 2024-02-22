import numpy
import time
from ruamel.yaml import YAML
from multiprocessing.shared_memory import SharedMemory
from voxel.processes.max_projection import MaxProjection

if __name__ == '__main__':

    chunk_size_frames = 64
    num_frames = 256
    img_shape = (2048, 2048)
        
    max_projection = MaxProjection()

    max_projection.row_count_px = img_shape[0]
    max_projection.column_count_px = img_shape[1]
    max_projection.frame_count_px = num_frames
    max_projection.projection_count_px = 64
    max_projection.data_type = 'uint16'
    max_projection.filename = 'test'
    max_projection.path = '.'

    img_bytes = numpy.prod(img_shape)*numpy.dtype('uint16').itemsize

    mip_buffer = SharedMemory(create=True, size=int(img_bytes))
    mip_image = numpy.ndarray(img_shape, dtype='uint16', buffer=mip_buffer.buf)

    max_projection.prepare(mip_buffer.name)
    max_projection.start()

    # Images arrive serialized in repeating channel order.
    for stack_index in range(num_frames):
        frame = \
        numpy.random.randint(
            low=0,
            high=256,
            size=img_shape,
            dtype = 'uint16'
        )
        
        stack_index += 1

        while max_projection.new_image.is_set():
            time.sleep(0.1)
        mip_image[:,:] = frame
        max_projection.new_image.set()

    max_projection.wait_to_finish()
    max_projection.close()
    mip_buffer.close()
    mip_buffer.unlink()
    del mip_buffer