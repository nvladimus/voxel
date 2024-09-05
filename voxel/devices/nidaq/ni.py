from functools import lru_cache
from typing import List, Tuple, Dict

import nidaqmx
from nidaqmx.constants import AcquisitionType, Edge

from voxel.devices.nidaq.base import VoxelDAQ
from voxel.devices.nidaq.task import DAQTask, DAQTaskType, DAQTaskChannel, DAQTaskTriggerMode, DAQTaskTriggerEdge


# TODO: Add Buffer management
# TODO: Add methods for asynchronous task execution e.g. wait_for_task_completion()
# TODO: Allow Task and Channel manipulation and improve their validation
# TODO: Consider caching channel waveforms.
#   but be careful with memory usage especially if channel and task configurations are dynamic
# TODO: Consider creating a context manager either for device or specific tasks (or specific tasks running)
#   Do we need to track task state? e.g. configured, running, stopped, etc.
# TODO: Add support for more task types


class VoxelNIDAQ(VoxelDAQ):
    def __init__(self, id: str, conn: str, simulated: bool = False):
        super().__init__(id)
        devices = self.get_available_devices()
        conn = conn if not simulated else next((device for device in devices if 'Sim' in device), None)
        self.device_name = conn
        self.tasks: Dict[str, DAQTask] = {}
        self.log.info('resetting nidaq')
        self.device.reset_device()

    def __repr__(self):
        return (f"{self.__class__.__name__} {self.device_name} \n"
                f"Tasks: {list(self.tasks.keys())}")

    @property
    @lru_cache(maxsize=1)
    def device(self) -> nidaqmx.system.device.Device:
        return nidaqmx.system.device.Device(self.device_name)

    @property
    def co_physical_chans(self) -> List[str]:
        return self.device.co_physical_chans.channel_names

    @property
    def ao_physical_chans(self) -> List[str]:
        return self.device.ao_physical_chans.channel_names

    @property
    def ao_rate_range(self) -> Tuple[float, float]:
        return self.device.ao_max_rate, self.device.ao_min_rate

    @property
    def ao_voltage_range(self) -> Tuple[float, float]:
        return self.device.ao_voltage_rngs[1], self.device.ao_voltage_rngs[0]

    @property
    def do_physical_chans(self) -> List[str]:
        return self.device.do_ports.channel_names

    @property
    def dio_ports(self) -> List[str]:
        return [channel.replace(f'port', "PFI") for channel in self.device.do_ports.channel_names]

    @property
    def dio_lines(self) -> List[str]:
        return self.device.di_lines.channel_names

    @property
    def do_rate_range(self) -> Tuple[float, float]:
        return self.device.do_max_rate, self.device.do_min_rate

    def is_valid_port(self, port: str, task_type) -> bool:
        port = self.device_name + '/' + port
        if task_type == DAQTaskType.AO:
            return port in self.ao_physical_chans
        elif task_type == DAQTaskType.DO:
            return port in self.do_physical_chans
        elif task_type == DAQTaskType.CO:
            return port in self.co_physical_chans

    def register_task(self, task: DAQTask):
        if task.name in self.tasks:
            # If the task already exists, close and remove it
            self.tasks[task.name].hardware_task.close()
            del self.tasks[task.name]

        task.hardware_task = nidaqmx.Task(task.name)

        def configure_timing(task: DAQTask):
            samples_per_channel = int(task.sampling_frequency_hz * task.period_time_ms / 1000)
            task.hardware_task.timing.cfg_samp_clk_timing(
                rate=task.sampling_frequency_hz,
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=samples_per_channel
            )

        def configure_trigger(task: DAQTask):
            if task.trigger_mode == DAQTaskTriggerMode.ON and task.trigger_source:
                trigger_edge = Edge.RISING if task.trigger_edge == DAQTaskTriggerEdge.RISING else Edge.FALLING
                task.hardware_task.triggers.start_trigger.cfg_dig_edge_start_trig(
                    trigger_source=f'/{self.device_name}/{task.trigger_source}',
                    trigger_edge=trigger_edge
                )
                task.hardware_task.triggers.start_trigger.retriggerable = task.retriggerable

        def create_ao_channel(task: DAQTask, channel: DAQTaskChannel):
            task.hardware_task.ao_channels.add_ao_voltage_chan(f"/{self.device_name}/{channel.port}")

        def create_do_channel(task: DAQTask, channel: DAQTaskChannel):
            task.hardware_task.do_channels.add_do_chan(f"/{self.device_name}/{channel.port}")

        def create_co_channel(task: DAQTask, channel: DAQTaskChannel):
            task.hardware_task.co_channels.add_co_pulse_chan_freq(
                f"/{self.device_name}/{channel.port}",
                freq=task.waveform_frequency_hz,
                duty_cycle=task.get_duty_cycle(channel.name)
            )

        channel_generators = {
            DAQTaskType.AO: create_ao_channel,
            DAQTaskType.DO: create_do_channel,
            DAQTaskType.CO: create_co_channel
        }

        if task.channels.values():
            for channel in task.channels.values():
                channel_generators[task.task_type](task, channel)
            configure_timing(task)
            configure_trigger(task)

        self.tasks[task.name] = task

    def start_task(self, task_name: str):
        try:
            task = self.tasks[task_name]
            if not task.channels:
                raise ValueError(f"Unable to start {task.name} task. No channels present.")
            if task.hardware_task:
                task.hardware_task.start()
        except KeyError:
            raise ValueError(f"Task {task_name} not found in DAQ manager.")

    def stop_task(self, task_name: str):
        try:
            task = self.tasks[task_name]
            if task.hardware_task:
                task.hardware_task.stop()
        except KeyError:
            raise ValueError(f"Task {task_name} not found in DAQ manager.")

    def write_task_waveforms(self, task_name: str):
        try:
            task = self.tasks[task_name]
            if task.hardware_task:
                waveforms = task.generate_waveforms()
                if task.task_type in [DAQTaskType.AO, DAQTaskType.DO]:
                    task.hardware_task.write(list(waveforms.values()), auto_start=True)
        except KeyError:
            raise ValueError(f"Task {task_name} not found in DAQ manager.")

    def close_task(self, task_name: str):
        try:
            task = self.tasks[task_name]
            if task.hardware_task:
                task.hardware_task.close()
            del self.tasks[task_name]
        except KeyError:
            raise ValueError(f"Task {task_name} not found in DAQ manager.")

    def close(self):
        for task in self.tasks.values():
            if task.hardware_task:
                task.hardware_task.close()
        self.tasks.clear()

    @staticmethod
    def get_available_devices():
        return [device.name for device in nidaqmx.system.System.local().devices]
