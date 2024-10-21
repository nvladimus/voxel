from functools import lru_cache

import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, Edge, Level, TaskMode

from voxel.core.instrument.daq.base import VoxelDAQ
from voxel.core.instrument.daq.task import (
    DAQTaskSampleMode,
    DAQTaskTriggerEdge,
    DAQTaskTriggerMode,
    DAQTaskType,
    VoxelDAQTask,
    VoxelDAQTaskChannel,
)

# Extras
# TODO: Consider caching channel waveforms.
#   but be careful with memory usage especially if channel and task configurations are dynamic
# TODO: Consider creating a context manager either for device or specific tasks (or specific tasks running)
#   Do we need to track task state? e.g. configured, running, stopped, etc.
# TODO: Add support for more task types


type HardwareTask = nidaqmx.Task


class VoxelNIDAQ(VoxelDAQ):
    def __init__(self, name: str, conn: str, simulated: bool = False):
        super().__init__(name)
        devices = self.get_available_devices()
        conn = conn if not simulated else next((device for device in devices if "Sim" in device), None)
        self.device_name = conn
        self.tasks: dict[str, VoxelDAQTask] = {}
        self.log.info("resetting nidaq")
        self.device.reset_device()

    def __repr__(self):
        return f"{self.__class__.__name__} {self.device_name} \n" f"Tasks: {list(self.tasks.keys())}"

    @property
    @lru_cache(maxsize=1)
    def device(self) -> nidaqmx.system.device.Device:
        return nidaqmx.system.device.Device(self.device_name)

    @property
    def co_physical_chans(self) -> list[str]:
        return self.device.co_physical_chans.channel_names

    @property
    def ao_physical_chans(self) -> list[str]:
        return self.device.ao_physical_chans.channel_names

    @property
    def ao_rate_range(self) -> tuple[float, float]:
        return self.device.ao_max_rate, self.device.ao_min_rate

    @property
    def ao_voltage_range(self) -> tuple[float, float]:
        return self.device.ao_voltage_rngs[1], self.device.ao_voltage_rngs[0]

    @property
    def do_physical_chans(self) -> list[str]:
        return self.device.do_ports.channel_names

    @property
    def dio_ports(self) -> list[str]:
        return [channel.replace(f"port", "PFI") for channel in self.device.do_ports.channel_names]

    @property
    def dio_lines(self) -> list[str]:
        return self.device.di_lines.channel_names

    @property
    def do_rate_range(self) -> tuple[float, float]:
        return self.device.do_max_rate, self.device.do_min_rate

    def is_valid_port(self, port: str, task_type) -> bool:
        port = self.device_name + "/" + port
        if task_type == DAQTaskType.AO:
            return port in self.ao_physical_chans
        elif task_type == DAQTaskType.DO:
            return port in self.do_physical_chans
        elif task_type == DAQTaskType.CO:
            return port in self.co_physical_chans

    def register_task(self, task: VoxelDAQTask):
        if task.name in self.tasks:
            # If the task already exists, close and remove it
            self.tasks[task.name].hardware_task.close()
            del self.tasks[task.name]

        task.hardware_task = nidaqmx.Task(task.name)

        def configure_timing(task: VoxelDAQTask):
            samples_per_channel = int(task.sampling_frequency_hz * task.period_time_ms / 1000)
            task.hardware_task.timing.cfg_samp_clk_timing(
                rate=task.sampling_frequency_hz,
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=samples_per_channel,
            )

        def configure_trigger(task: VoxelDAQTask):
            if task.task_type == DAQTaskType.CO:
                if task.trigger_mode == DAQTaskTriggerMode.OFF:
                    # TODO: Figure out how to pass in pulse_count
                    pulse_count = {"sample_mode": DAQTaskSampleMode.CONTINUOUS}
                    task.hardware_task.timing.cfg_implicit_timing(**pulse_count)
                else:
                    raise ValueError(f"Trigger mode {task.trigger_mode.name} not supported for CO tasks.")
            elif task.task_type in [DAQTaskType.AO, DAQTaskType.DO]:
                if task.trigger_mode == DAQTaskTriggerMode.ON and task.trigger_source:
                    trigger_edge = Edge.RISING if task.trigger_edge == DAQTaskTriggerEdge.RISING else Edge.FALLING
                    task.hardware_task.triggers.start_trigger.cfg_dig_edge_start_trig(
                        trigger_source=f"/{self.device_name}/{task.trigger_source}", trigger_edge=trigger_edge
                    )
                    task.hardware_task.triggers.start_trigger.retriggerable = task.retriggerable

        def create_ao_channel(task: VoxelDAQTask, channel: VoxelDAQTaskChannel):
            task.hardware_task.ao_channels.add_ao_voltage_chan(f"/{self.device_name}/{channel.port}")

        def create_do_channel(task: VoxelDAQTask, channel: VoxelDAQTaskChannel):
            task.hardware_task.do_channels.add_do_chan(f"/{self.device_name}/{channel.port}")

        def create_co_channel(task: VoxelDAQTask, channel: VoxelDAQTaskChannel):
            task.hardware_task.co_channels.add_co_pulse_chan_freq(
                f"/{self.device_name}/{channel.port}",
                freq=task.waveform_frequency_hz,
                duty_cycle=task.get_duty_cycle(channel.name),
            )

        channel_generators = {
            DAQTaskType.AO: create_ao_channel,
            DAQTaskType.DO: create_do_channel,
            DAQTaskType.CO: create_co_channel,
        }

        if task.channels.values():
            for channel in task.channels.values():
                channel_generators[task.task_type](task, channel)
            configure_timing(task)
            configure_trigger(task)

        # TODO: Figure out how to handle the following
        setattr(task.hardware_task, f"{task.task_type.lower()}_line_states_done_state", Level.LOW)
        setattr(task.hardware_task, f"{task.task_type.lower()}_line_states_paused_state", Level.LOW)

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

    def wait_until_task_is_done(self, task_name: str, timeout=1.0):
        try:
            task = self.tasks[task_name]
            if task.hardware_task:
                task.hardware_task.wait_until_done(timeout)
        except KeyError:
            raise ValueError(f"Task {task_name} not found in DAQ manager.")

    def is_task_done(self, task_name: str):
        try:
            task = self.tasks[task_name]
            if task.hardware_task:
                return task.hardware_task.is_task_done()
        except KeyError:
            raise ValueError(f"Task {task_name} not found in DAQ manager.")

    def write_task_waveforms(self, task_name: str):

        def rereserve_buffer(task: VoxelDAQTask, buffer_size: int):
            if task.hardware_task:
                task.hardware_task.control(TaskMode.TASK_UNRESERVE)
                task.hardware_task.out_stream.output_buf_size = buffer_size
                task.hardware_task.control(TaskMode.TASK_COMMIT)

        try:
            task = self.tasks[task_name]
            if task.hardware_task:
                waveforms = task.generate_waveforms()
                match task.task_type:
                    case DAQTaskType.AO | DAQTaskType.DO:
                        # Get the channel names directly from the hardware task
                        channel_names = task.hardware_task.channel_names

                        if len(waveforms) != len(channel_names):
                            raise ValueError(
                                f"Number of waveforms ({len(waveforms)}) "
                                f"does not match number of channels ({len(channel_names)})"
                            )

                        # Organize waveforms based on the hardware task's channel order
                        ordered_waveforms = []
                        for full_channel_name in channel_names:
                            channel_name = full_channel_name.split("/")[-1]
                            if channel_name not in waveforms:
                                raise ValueError(f"Waveform for channel {channel_name} not found")
                            ordered_waveforms.append(waveforms[channel_name])

                        self.log.debug(f"Writing waveforms for task {task_name} in order: {channel_names}")

                        if task.hardware_task.is_task_done():
                            rereserve_buffer(task, len(ordered_waveforms[0]))
                        print(np.array(ordered_waveforms))
                        task.hardware_task.write(np.array(ordered_waveforms), auto_start=False)
                    case _:
                        self.log.warning(f"Task {task_name} not supported for waveform writing.")
        except KeyError:
            raise ValueError(f"Task {task_name} not found in DAQ manager.")

    def close_task(self, task_name: str):
        try:
            task = self.tasks[task_name]
            if task.hardware_task:
                task.hardware_task.close()
        except KeyError:
            pass  # Task already closed

    def close(self):
        for task in self.tasks.values():
            self.close_task(task.name)
        self.tasks.clear()

    @staticmethod
    def get_available_devices():
        return [device.name for device in nidaqmx.system.System.local().devices]
