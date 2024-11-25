from dataclasses import dataclass
from abc import ABC, abstractmethod
from voxel.instrument.frame_stack import FrameStack
from voxel.utils.vec import Vec2D
from voxel.utils.log_config import get_logger

from .plan import VoxelAcquisitionPlanner


@dataclass
class AcquisitionState:
    progress: dict[Vec2D, list[float]]


# TODO: Figure out what the relationship between engine and manager should be.
class VoxelAcquisitionEngine(ABC):
    def __init__(self, plan: VoxelAcquisitionPlanner) -> None:
        self.plan = plan
        self.instrument = self.plan.instrument
        self.log = get_logger(self.__class__.__name__)
        self._current_tile: Vec2D | None = None

    @abstractmethod
    def run(self):
        pass

    def setup_directories(self): ...

    def validate_acquisition_plan(self):
        # Validate that the plan is compatible with the instrument
        #   - Check that the position of the frame_stacks is within the limits of the stage
        #   - Check that the channels in the plan are available in the instrument
        ...

    def check_local_disk_space(self, frame_stack: "FrameStack") -> bool:
        # Check that there is enough disk space to save the frames
        ...

    def check_external_disk_space(self, frame_stack: "FrameStack") -> bool:
        # Check that there is enough disk space to save the frames
        ...

    @property
    @abstractmethod
    def state(self) -> AcquisitionState:
        pass
