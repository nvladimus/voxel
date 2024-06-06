from abc import ABC, abstractmethod
import logging
from typing import Literal

from pydantic import BaseModel

class FlipMountConfig(BaseModel):
    id: str
    conn: str
    positions: dict[str, Literal[0, 1]]
    init_pos: str
    init_flip_time_ms: int

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
        """Return the current position of the flip mount."""
        pass

    @position.setter
    @abstractmethod
    def position(self, position_name: str, wait=False):
        pass

    @abstractmethod
    def toggle(self):
        pass

    @property
    @abstractmethod
    def flip_time_ms(self) -> int:
        pass

    @flip_time_ms.setter
    @abstractmethod
    def flip_time_ms(self, time_ms: int):
        pass