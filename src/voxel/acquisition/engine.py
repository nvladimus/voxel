from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, List

from voxel import VoxelInstrument
from voxel.acquisition.model.frame_stack import FrameStack
from voxel.acquisition.manager import VoxelAcquisitionPlan
from voxel.utils.geometry.vec import Vec2D
from voxel.utils.logging import get_logger


@dataclass
class AcquisitionState:
    progress: Dict[Vec2D, List[float]]


# TODO: Figure out what the relationship between engine and manager should be.
class VoxelAcquisitionEngine(ABC):
    def __init__(self, plan: VoxelAcquisitionPlan, instrument: VoxelInstrument) -> None:
        self.plan = plan
        self.instrument = instrument
        self.log = get_logger(self.__class__.__name__)
        self._current_tile: Optional[Vec2D] = None

    @abstractmethod
    def run(self):
        pass

    def setup_directories(self):
        pass

    def validate_acquisition_plan(self):
        # Validate that the plan is compatible with the instrument
        #   - Check that the position of the frame_stacks is within the limits of the stage
        #   - Check that the channels in the plan are available in the instrument
        pass

    def check_local_disk_space(self, frame_stack: 'FrameStack') -> bool:
        # Check that there is enough disk space to save the frames
        pass

    def check_external_disk_space(self, frame_stack: 'FrameStack') -> bool:
        # Check that there is enough disk space to save the frames
        pass

    @property
    @abstractmethod
    def state(self) -> AcquisitionState:
        pass
