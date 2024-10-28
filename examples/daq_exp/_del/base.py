from abc import abstractmethod
from typing import TYPE_CHECKING

from voxel.core.instrument.device import VoxelDevice

if TYPE_CHECKING:
    from voxel.core.instrument.daq.task import VoxelDAQTask


# Extras
# TODO: Consider caching channel waveforms.
#   but be careful with memory usage especially if channel and task configurations are dynamic
# TODO: Consider creating a context manager either for device or specific tasks (or specific tasks running)
#   Do we need to track task state? e.g. configured, running, stopped, etc.
# TODO: Add support for more task types


class VoxelDAQ(VoxelDevice):
    def __init__(self, name: str):
        super().__init__(name)
        self.tasks: dict[str, VoxelDAQTask] = {}

    @property
    @abstractmethod
    def co_physical_chans(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def ao_physical_chans(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def ao_rate_range(self) -> tuple[float, float]:
        pass

    @property
    @abstractmethod
    def ao_voltage_range(self) -> tuple[float, float]:
        pass

    @property
    @abstractmethod
    def do_physical_chans(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def dio_ports(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def dio_lines(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def do_rate_range(self) -> tuple[float, float]:
        pass

    @abstractmethod
    def is_valid_port(self, port: str, task_type) -> bool:
        pass

    @abstractmethod
    def register_task(self, task: "VoxelDAQTask"):
        pass

    @abstractmethod
    def start_task(self, task_name: str):
        pass

    @abstractmethod
    def stop_task(self, task_name: str):
        pass

    @abstractmethod
    def wait_until_task_is_done(self, task_name: str, timeout=1.0):
        pass

    @abstractmethod
    def is_task_done(self, task_name: str):
        pass

    @abstractmethod
    def write_task_waveforms(self, task_name: str):
        pass

    @abstractmethod
    def close_task(self, task_name: str):
        pass

    @abstractmethod
    def close(self):
        pass
