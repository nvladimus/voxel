import numpy
import cupy
from cucim.skimage.transform import downscale_local_mean

class DownSample2D:

    def __init__(self, binning: int = 2):
        # downscaling factor
        self._binning = binning

    def run(self, image: numpy.array):
            # convert numpy to cupy array
            image = cupy.asarray(image)
            downsampled_image = downscale_local_mean(image, factors=(self._binning, self._binning))
            return downsampled_image