from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, List

from voxel import VoxelInstrument
from voxel.acquisition.planner import AcquisitionPlan
from voxel.utils.geometry.vec import Vec2D
from voxel.utils.logging import get_logger


@dataclass
class AcquisitionState:
    progress: Dict[Vec2D, List[float]]


class VoxelAcquisitionEngine(ABC):
    def __init__(self, plan: AcquisitionPlan, instrument: VoxelInstrument) -> None:
        self.plan = plan
        self.instrument = instrument
        self.log = get_logger(self.__class__.__name__)
        self._current_tile: Optional[Vec2D] = None

    @abstractmethod
    def run(self):
        pass

    @property
    @abstractmethod
    def state(self) -> AcquisitionState:
        pass
