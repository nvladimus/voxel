from typing import List, Tuple, Dict

from voxel.instrument.nidaq import DAQTask, DAQTaskType
from voxel.instrument.nidaq.base import VoxelDAQ


class SimulatedHardwareTask:
    def __init__(self, name: str):
        self.name = name
        self.is_running = False

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

    def close(self):
        self.is_running = False


class SimulatedNIDAQ(VoxelDAQ):
    def __init__(self, name: str, conn: str):
        super().__init__(name)
        self.device_name = conn
        self.tasks: Dict[str, DAQTask] = {}
        self.hardware_tasks: Dict[str, SimulatedHardwareTask] = {}

    def __repr__(self):
        return f"SimulatedNIDAQ {self.device_name}\nTasks: {list(self.tasks.keys())}"

    @property
    def co_physical_chans(self) -> List[str]:
        return [f"{self.device_name}/ctr0", f"{self.device_name}/ctr1"]

    @property
    def ao_physical_chans(self) -> List[str]:
        ports = [ 'ao0', 'ao1', 'ao2', 'ao3', 'ao4', 'ao5', 'ao6', 'ao7', 'ao8', 'ao9', 'ao10', 'ao11', 'ao12']
        return [f"{self.device_name}/{port}" for port in ports]

    @property
    def ao_rate_range(self) -> Tuple[float, float]:
        return 1000000.0, 1.0

    @property
    def ao_voltage_range(self) -> Tuple[float, float]:
        return 10.0, -10.0

    @property
    def do_physical_chans(self) -> List[str]:
        return [f"{self.device_name}/port0/line0", f"{self.device_name}/port0/line1"]

    @property
    def dio_ports(self) -> List[str]:
        return ["PFI0", "PFI1"]

    @property
    def dio_lines(self) -> List[str]:
        return [f"{self.device_name}/port0/line0", f"{self.device_name}/port0/line1"]

    @property
    def do_rate_range(self) -> Tuple[float, float]:
        return 1000000.0, 1.0

    def is_valid_port(self, port: str, task_type: DAQTaskType) -> bool:
        full_port = f"{self.device_name}/{port}"
        if task_type == DAQTaskType.AO:
            return full_port in self.ao_physical_chans
        elif task_type == DAQTaskType.DO:
            return full_port in self.do_physical_chans
        elif task_type == DAQTaskType.CO:
            return full_port in self.co_physical_chans
        return False

    def register_task(self, task: DAQTask):
        self.tasks[task.name] = task
        self.hardware_tasks[task.name] = SimulatedHardwareTask(task.name)
        task.hardware_task = self.hardware_tasks[task.name]
        print(f"Registered task: {task.name}")

    def start_task(self, task_name: str):
        if task_name in self.tasks:
            hardware_task = self.hardware_tasks[task_name]
            hardware_task.start()
            print(f"Started task: {task_name}")
        else:
            raise ValueError(f"Task {task_name} not found")

    def stop_task(self, task_name: str):
        if task_name in self.tasks:
            hardware_task = self.hardware_tasks[task_name]
            hardware_task.stop()
            print(f"Stopped task: {task_name}")
        else:
            raise ValueError(f"Task {task_name} not found")

    def wait_until_task_is_done(self, task_name: str, timeout: float = 1.0):
        if task_name in self.tasks:
            print(f"Waiting for task {task_name} to complete (simulated)")
        else:
            raise ValueError(f"Task {task_name} not found")

    def is_task_done(self, task_name: str) -> bool:
        if task_name in self.tasks:
            hardware_task = self.hardware_tasks[task_name]
            return not hardware_task.is_running
        else:
            raise ValueError(f"Task {task_name} not found")

    def write_task_waveforms(self, task_name: str):
        if task_name in self.tasks:
            task = self.tasks[task_name]
            waveforms = task.generate_waveforms()
            print(f"Writing waveforms for task: {task_name}")
            for port, waveform in waveforms.items():
                print(f"Channel: {port}, Waveform shape: {waveform.shape}")
        else:
            raise ValueError(f"Task {task_name} not found")

    def close_task(self, task_name: str):
        if task_name in self.tasks:
            hardware_task = self.hardware_tasks[task_name]
            hardware_task.close()
            del self.tasks[task_name]
            del self.hardware_tasks[task_name]
            print(f"Closed task: {task_name}")
        else:
            print(f"Task {task_name} not found or already closed")

    def close(self):
        for task_name in list(self.tasks.keys()):
            self.close_task(task_name)
        print("All tasks closed")

    @staticmethod
    def get_available_devices():
        return ["Dev1", "Dev2"]
