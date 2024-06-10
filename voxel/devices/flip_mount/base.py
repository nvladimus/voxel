from abc import ABC, abstractmethod
import logging
from typing import Literal

from pydantic import BaseModel, field_validator

class FlipMountConfig(BaseModel):
    id: str
    conn: str
    positions: dict[str, Literal[0, 1]]
    init_pos: str
    init_flip_time_ms: int

    @field_validator('init_pos')
    def init_pos_must_be_in_positions(cls, init_pos, values):
        positions = values.get('positions')
        if positions is not None and init_pos not in positions:
            raise ValueError(f'init_pos {init_pos} is not a key in positions dictionary')
        return init_pos

class BaseFlipMount(ABC):
    def __init__(self, id: str):
        self.id = id
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)

    @abstractmethod
    def connect(self):
        """Connect to the flip mount."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from the flip mount."""
        pass

    @property
    @abstractmethod
    def position(self) -> str | None:
        """Position of the flip mount."""
        pass

    @position.setter
    @abstractmethod
    def position(self, position_name: str, wait=False):
        pass

    @abstractmethod
    def toggle(self):
        """Toggle the flip mount position """
        pass

    @property
    @abstractmethod
    def flip_time_ms(self) -> int:
        """Time it takes to flip the mount in milliseconds."""
        pass

    @flip_time_ms.setter
    @abstractmethod
    def flip_time_ms(self, time_ms: int):
        pass

    def __del__(self):
            self.disconnect()

# Path: voxel/devices/flip_mount/thorlabs_mff101.py