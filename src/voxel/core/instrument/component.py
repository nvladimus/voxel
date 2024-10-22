from abc import ABC
from voxel.core.utils.logging import get_logger


class VoxelComponent(ABC):
    def __init__(self, name: str) -> None:
        self.log = get_logger(f"{self.__class__.__name__}[{self.name}]")
        self.name = name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.name}"
