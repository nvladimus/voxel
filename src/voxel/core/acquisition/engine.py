from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from voxel.core.utils.geometry.vec import Vec2D
from voxel.core.utils.log_config import get_logger

from ..instrument import VoxelInstrument
from .model.frame_stack import FrameStack
from .model.plan import VoxelAcquisitionPlan


@dataclass
class AcquisitionState:
    progress: dict[Vec2D, list[float]]


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

    def check_local_disk_space(self, frame_stack: "FrameStack") -> bool:
        # Check that there is enough disk space to save the frames
        pass

    def check_external_disk_space(self, frame_stack: "FrameStack") -> bool:
        # Check that there is enough disk space to save the frames
        pass

    @property
    @abstractmethod
    def state(self) -> AcquisitionState:
        pass
