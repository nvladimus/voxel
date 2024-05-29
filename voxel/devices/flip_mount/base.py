from abc import ABC, abstractmethod
import logging

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
    def position(self) -> str:
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
    def switch_time_ms(self) -> float:
        pass

    @switch_time_ms.setter
    @abstractmethod
    def switch_time_ms(self, time_ms: float):
        pass