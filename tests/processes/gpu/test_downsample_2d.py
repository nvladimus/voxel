import numpy
from exa_spim_refactor.processes.gpu.downsample_2d import DownSample2D

image = numpy.random.randint(low=128, high=256, size=(2048, 2048), dtype='uint16')
print(f'original image size: {image.shape}')
gpu_binning = DownSample2D(binning=2)
binned_image = gpu_binning.run(image)
print(f'downsampled image size: {binned_image.shape}')