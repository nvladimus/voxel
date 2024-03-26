import numpy
import tensorstore as ts

class DownSample3D:

    def __init__(self, binning: int = 2):
        # downscaling factor
        self._binning = binning

    def run(self, image: numpy.array):
        downsampled_image = ts.downsample(ts.array(image),
                                          downsample_factors=[self._binning, self._binning, self._binning],
                                          method="mean").read().result()
        return downsampled_image