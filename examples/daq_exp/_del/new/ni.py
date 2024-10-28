from functools import lru_cache

import nidaqmx

from voxel.core.instrument.daq._del.new.base import VoxelDAQ, VoxelDAQTask


class VoxelNiDAQTask(VoxelDAQTask):
    """A NiDAQ implementation of a VoxelDAQTask.
    :param name: The name of the task.
    :param daq: The DAQ device the task is associated with.
    :param sampling_frequency_hz: The sampling frequency of the task in Hz.
    :param period_ms: The period of the task in ms.
    :type name: str
    :type daq: VoxelNiDAQ
    :type sampling_frequency_hz: float
    :type period_ms: float
    """

    def __init__(self, name: str, daq: "VoxelNiDAQ", sampling_frequency_hz: float, period_ms: float) -> None:
        super().__init__(name, daq, sampling_frequency_hz, period_ms)
        self.hardware_task = None


class VoxelNiDAQ(VoxelDAQ):
    def __init__(self, conn: str, name: str = "VoxelNiDAQ") -> None:
        super().__init__(name)
        self.device_name = conn
        self.tasks: dict[str, VoxelNiDAQTask] = {}
        self.device.reset_device()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.device_name} \n" f"Tasks: {list(self.tasks.keys())}"

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__} {self.device_name} \n"
            f"Tasks: {list(self.tasks.keys())} \n"
            f"Available Ports: \n"
            f"  AO: {self.ao_ports} \n"
            f"  DO: {self.do_ports} \n"
            f"  CO: {self.co_ports} \n"
            f"  DI: {self.di_lines} \n"
        )

    @property
    @lru_cache(maxsize=1)
    def device(self) -> nidaqmx.system.device.Device:
        return nidaqmx.system.device.Device(self.device_name)

    @property
    def ao_ports(self) -> list[str]:
        return [port.split("/")[1] for port in self.device.ao_physical_chans.channel_names]

    @property
    def do_ports(self) -> list[str]:
        return [port.split("/")[1].replace("port", "PFI") for port in self.device.do_ports.channel_names]

    @property
    def co_ports(self) -> list[str]:
        return [port.split("/")[1] for port in self.device.co_physical_chans.channel_names]

    @property
    def di_lines(self) -> list[str]:
        return [port.split("/", 1)[1] for port in self.device.di_lines.channel_names]

    @property
    def ao_rate_range(self) -> tuple[float, float]:
        return self.device.ao_min_rate, self.device.ao_max_rate

    @property
    def ao_voltage_range(self) -> tuple[float, float]:
        return self.device.ao_voltage_rngs[1], self.device.ao_voltage_rngs[0]

    @property
    def do_rate_range(self) -> tuple[float, float]:
        return self.device.do_min_rate, self.device.do_max_rate

    def is_port_available(self, port_id) -> bool:
        ports = [port for port_list in self.ports.values() for port in port_list]
        return port_id in ports

    def register_task(self, task: VoxelNiDAQTask) -> None:
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists.")
        self.tasks[task.name] = task

    # def __del__(self) -> None:
    #     for task in self.tasks.values():
    #         task.close()


if __name__ == "__main__":
    daq = VoxelNiDAQ("Dev1")
    # task = nidaqmx.Task("TestTask")
    # daq.tasks["TestTask"] = task
    # print(task.timing)
    # print(task.triggers)
    # # print(daq)
    # task.close()
