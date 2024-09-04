from typing import Dict, List, Optional

import nidaqmx

from voxel.devices.nidaq import plot_waveforms
from voxel.devices.nidaq.task import DAQTask, TaskType, DAQTaskChannel
from voxel.devices.nidaq.waveforms import DAQWaveform, DAQWaveformConfig


class DAQManager:
    def __init__(self, device_name: str):
        self.device_name = device_name
        self.dev: nidaqmx.system.device.Device = None
        self.tasks: Dict[str, DAQTask] = {}
        self.initialize_device()

    def initialize_device(self):
        self.dev = nidaqmx.system.device.Device(self.device_name)
        # Add any necessary device initialization here

    def add_task(self, task: DAQTask):
        if task.name in self.tasks:
            raise ValueError(f"Task with name '{task.name}' already exists")
        self.tasks[task.name] = task

    def remove_task(self, task_name: str):
        task = self.tasks.pop(task_name, None)
        if task:
            task.close()

    def get_task(self, task_name: str) -> Optional[DAQTask]:
        return self.tasks.get(task_name)

    def get_tasks_by_type(self, task_type: TaskType) -> List[DAQTask]:
        return [task for task in self.tasks.values() if task.task_type == task_type]

    def create_nidaqmx_tasks(self):
        for task in self.tasks.values():
            task.create_nidaqmx_task()

    def start_task(self, task_name: str):
        task = self.tasks.get(task_name)
        if task:
            task.start()

    def stop_task(self, task_name: str):
        task = self.tasks.get(task_name)
        if task:
            task.stop()

    def write_waveforms(self, task_name: str):
        task = self.tasks.get(task_name)
        if task:
            task.write_waveforms()

    def close(self):
        for task in self.tasks.values():
            task.close()
        self.tasks.clear()

    @staticmethod
    def get_available_devices():
        return [device.name for device in nidaqmx.system.System.local().devices]


if __name__ == '__main__':
    # Create a DAQ manager
    daq_manager = DAQManager(device_name="Dev1")

    # Create a task
    ao_task = DAQTask(
        name="AO_Task",
        task_type=TaskType.AO,
        sampling_frequency_hz=350e3,
        period_time_ms=10,
        rest_time_ms=2,
        device_name=daq_manager.device_name
    )

    # Create channels
    square_channel = DAQTaskChannel(
        name="Square",
        port="ao0",
        waveform=DAQWaveform.SQUARE,
        center_volts=2.5,
        amplitude_volts=5,
        frequency_hz=1000,
        start_time=0,
        end_time=5
    )

    triangle_channel = DAQTaskChannel(
        name="Triangle",
        port="ao1",
        waveform=DAQWaveform.TRIANGLE,
        center_volts=2.5,
        amplitude_volts=5,
        frequency_hz=1000,
        start_time=0,
        end_time=5
    )

    # Add channels to the task
    ao_task.add_channel(square_channel)
    ao_task.add_channel(triangle_channel)

    # # Add the task to the DAQ manager
    # daq_manager.add_task(ao_task)
    #
    # # Create NI-DAQmx tasks
    # daq_manager.create_nidaqmx_tasks()
    #
    # # Write waveforms to the hardware
    # daq_manager.write_waveforms("AO_Task")
    #
    # # Start the task
    # daq_manager.start_task("AO_Task")
    #
    # # ... (perform other operations)
    #
    # # Stop the task
    # daq_manager.stop_task("AO_Task")
    #
    # # Close and cleanup
    # daq_manager.close()

    # Generate waveforms for plotting
    plt_task = ao_task
    plt_channel = square_channel
    waveforms = plt_task.generate_waveforms()
    print(f"Generated waveform for {plt_channel.name}: {waveforms[plt_channel.name].shape}")
    for channel_name, waveform in waveforms.items():
        print(f"Generated waveform for {channel_name}: {waveform.shape}")

    plotting_cfg = DAQWaveformConfig(
        sampling_frequency_hz=plt_task.sampling_frequency_hz,
        period_time_ms=plt_task.period_time_ms,
        rest_time_ms=plt_task.rest_time_ms,
        start_time_ms=plt_channel.start_time,
        end_time_ms=plt_channel.end_time,
        center_volts=plt_channel.center_volts,
        amplitude_volts=plt_channel.amplitude_volts,
        frequency_hz=plt_channel.frequency_hz
    )

    plot_waveforms(waveforms, plotting_cfg, num_cycles=2)
