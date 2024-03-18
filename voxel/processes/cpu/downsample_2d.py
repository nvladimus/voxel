import numpy

class DownSample2D:

    def __init__(self, binning: int = 2):
        # downscaling factor
        if binning != 2:
            raise ValueError('cpu downsampling only supports binning=2')

    def run(self, image: numpy.array):
        downsampled_image = (image[0::2, 0::2] + \
                             image[1::2, 0::2] + \
                             image[0::2, 1::2] + \
                             image[1::2, 1::2]) // 4
        return downsampled_image