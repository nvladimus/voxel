from abc import ABC, abstractmethod
from dataclasses import dataclass

from acquisition.acquisition import VoxelAcquisition
from utils.logging import get_logger

@dataclass
class VoxelAcquisitionState:
    progress: float

class VoxelAcquisitionEngine(ABC):

    def __init__(self, acquisition: VoxelAcquisition):
        self.log = get_logger(f"{self.__class__.__name__}")
        self.acquisition = acquisition

    @abstractmethod
    def run(self):
        pass

    @property
    @abstractmethod
    def state(self) -> VoxelAcquisitionState:
        pass