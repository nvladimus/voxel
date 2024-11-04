from abc import ABC, abstractmethod
from typing import Self

from nidaqmx.errors import DaqError, DaqResourceWarning
from nidaqmx.task import Task as NiTask

from voxel.core.utils.log_config import get_component_logger
from .daq import PinInfo, VoxelDaq


class VoxelDaqTask(ABC):
    def __init__(self, name: str, daq: "VoxelDaq") -> None:
        self.name = name
        self.inst = NiTask(name)
        self.daq = daq
        self.log = get_component_logger(self)

        self.daq.tasks[self.name] = self

    @property
    @abstractmethod
    def pins(self) -> list[PinInfo]:
        """List of pins used by this task."""
        pass

    def start(self) -> None:
        self.log.info("Starting task...")
        self.inst.start()

    def stop(self) -> None:
        self.log.info("Stopping task...")
        self.inst.stop()

    def close(self) -> None:
        try:
            for pin in self.pins:
                self.daq.release_pin(pin)
            if self.name in self.daq.tasks:
                del self.daq.tasks[self.name]
            self.inst.close()
        except DaqResourceWarning:
            self.log.debug("Task already closed or not initialized.")
        except DaqError as e:
            self.log.error(f"Error closing task: {e}")

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()
