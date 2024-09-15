from acquisition.acquisition import VoxelAcquisition
from utils.logging import get_logger


class VoxelRoutine:
    def __init__(self, acq: VoxelAcquisition):
        self.log = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.acq = acq

    def run(self):
        raise NotImplementedError