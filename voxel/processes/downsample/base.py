import numpy
from abc import abstractmethod


class BaseDownSample():
    """
    Base class for image downsampling.

    :param image: Input image
    :type image: numpy.array
    """

    def __init__(self, binning: int) -> None:
        self._binning = binning

    @abstractmethod
    def run(self, method, image: numpy.array):
        """
        Run function for image downsampling.

        :param image: Input image
        :type image: numpy.array
        """
        pass
