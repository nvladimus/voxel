from abc import abstractmethod
from typing import Dict, List, Tuple, TypeAlias, Union, TYPE_CHECKING

import nidaqmx

from voxel.devices import VoxelDevice

if TYPE_CHECKING:
    from voxel.devices.nidaq.task import DAQTask

HardwareDevice: TypeAlias = Union[nidaqmx.system.device.Device]  # Add other types as needed
HardwareTask: TypeAlias = Union[nidaqmx.Task]  # Add other types as needed


class VoxelDAQ(VoxelDevice):
    def __init__(self, id: str):
        super().__init__(id)
        self.tasks: Dict[str, 'DAQTask'] = {}

    @property
    @abstractmethod
    def device(self) -> HardwareDevice:
        pass

    @property
    @abstractmethod
    def co_physical_chans(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def ao_physical_chans(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def ao_rate_range(self) -> Tuple[float, float]:
        pass

    @property
    @abstractmethod
    def ao_voltage_range(self) -> Tuple[float, float]:
        pass

    @property
    @abstractmethod
    def do_physical_chans(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def dio_ports(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def dio_lines(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def do_rate_range(self) -> Tuple[float, float]:
        pass

    @abstractmethod
    def register_task(self, task: 'DAQTask'):
        pass

    @abstractmethod
    def start_task(self, task_name: str):
        pass

    @abstractmethod
    def stop_task(self, task_name: str):
        pass

    @abstractmethod
    def write_task_waveforms(self, task_name: str):
        pass
