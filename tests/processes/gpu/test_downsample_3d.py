import numpy
from exa_spim_refactor.processes.gpu.downsample_3d import DownSample3D

image = numpy.random.randint(low=128, high=256, size=(256, 256, 256), dtype='uint16')
print(f'original matrix size: {image.shape}')
gpu_binning = DownSample3D(binning=2)
binned_image = gpu_binning.run(image)
print(f'downsampled matrix size: {binned_image.shape}')