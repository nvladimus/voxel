import tensorstore as ts
import numpy as np
import time
from voxel.processes.gpu.gputools.downsample_3d import DownSample3D

# row_count = 10624
# column_count = 14080
# frame_count = 32
# chunk_size_x = 220
# chunk_size_y = 166
# chunk_size_z = 32
# levels = 4

row_count = 10624
column_count = 14080
frame_count = 64
chunk_size_x = 220
chunk_size_y = 188
chunk_size_z = 64
levels = 4

image = np.random.randn(frame_count, row_count, column_count)*5+200
image = image.astype('uint16')
gpu_binning = DownSample3D(binning=2)

stores = list()
for level in range(levels):
    stores.append(ts.open({"driver": "zarr3", "kvstore": f"file://D:/tmp/dataset/{level}", "create": True, "delete_existing": True},
                    chunk_layout = ts.ChunkLayout(read_chunk_shape=[chunk_size_z // 2**level, chunk_size_y, chunk_size_x],
                                                  write_chunk_shape=[frame_count // 2**level, row_count // 2**level, column_count // 2**level]),
                    dtype=ts.uint16,
                    shape=[frame_count // 2**level, row_count // 2**level, column_count // 2**level],
                    codec=ts.CodecSpec({"driver": "zarr3", "codecs": [{"name": "blosc",
                                                                       "configuration": {"cname": "lz4", "clevel": 1,
                                                                       "shuffle": "shuffle"}}]}),
                    ).result())

start_time = time.time()

write_futures = list()
for level in range(levels):
    if level > 0:
        # image = gpu_binning.run(image)
        image = (image[0::2, 0::2, 0::2] + \
                 image[1::2, 0::2, 0::2] + \
                 image[0::2, 1::2, 0::2] + \
                 image[0::2, 0::2, 1::2] + \
                 image[1::2, 1::2, 0::2] + \
                 image[0::2, 1::2, 1::2] + \
                 image[1::2, 0::2, 1::2] + \
                 image[1::2, 1::2, 1::2]) // 8

    write_futures.append(stores[level].write(image))

for level in range(levels):
    write_futures[level].result()

end_time = time.time()

total_bytes = row_count*column_count*frame_count*2
print('%g bytes/s (%g source bytes, %g elapsed seconds)' % (total_bytes / (end_time - start_time), total_bytes, end_time - start_time))