import numpy
import pyclesperanto as cle

class DownSample3D:

    def __init__(self, binning: int = 2):
        # downscaling factor
        self._binning = binning
        # get gpu device
        self._device = cle.select_device()

    def run(self, image: numpy.array):
            # move image to gpu
            input_image = cle.push(image)
            # run operation
            downsampled_image = cle.scale(input_image,
                                          factor_x=1/self._binning,
                                          factor_y=1/self._binning,
                                          factor_z=1/self._binning,
                                          device=self._device,
                                          resize=True)
            # move image off gpu and return
            return cle.pull(downsampled_image)