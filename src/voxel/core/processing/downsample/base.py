from abc import abstractmethod

import numpy

from voxel.core.utils.logging import get_logger


class BaseDownSample:
    """
    Base class for image downsampling.

    :param image: Input image
    :type image: numpy.array
    """

    def __init__(self, binning: int) -> None:
        self._binning = binning
        self.log = get_logger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def run(self, method, image: numpy.array):
        """
        Run function for image downsampling.

        :param method:
        :param image: Input image
        :type image: numpy.array
        """
        pass
