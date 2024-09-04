from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

import nidaqmx
from nidaqmx.constants import AcquisitionType
from numpy.typing import NDArray

from voxel.devices.nidaq.waveforms import DAQWaveform, DAQWaveformConfig


class TaskType(Enum):
    AO = "ao"
    DO = "do"
    CO = "co"


@dataclass
class DAQTaskChannel:
    name: str
    port: str
    waveform: DAQWaveform
    center_volts: float
    amplitude_volts: float
    frequency_hz: float
    start_time: float
    end_time: float


@dataclass
class DAQTask:
    name: str
    task_type: TaskType
    sampling_frequency_hz: float
    period_time_ms: float
    rest_time_ms: float
    device_name: str
    channels: Dict[str, DAQTaskChannel] = field(default_factory=dict)
    nidaqmx_task: Optional[nidaqmx.Task] = None

    def add_channel(self, channel: DAQTaskChannel):
        if channel.name in self.channels:
            raise ValueError(f"Channel with name '{channel.name}' already exists in this task")
        self.channels[channel.name] = channel

    def remove_channel(self, channel_name: str):
        self.channels.pop(channel_name, None)

    def get_channel(self, channel_name: str) -> Optional[DAQTaskChannel]:
        return self.channels.get(channel_name)

    def generate_waveforms(self) -> Dict[str, NDArray]:
        waveforms = {}
        for name, channel in self.channels.items():
            config = DAQWaveformConfig(
                sampling_frequency_hz=self.sampling_frequency_hz,
                period_time_ms=self.period_time_ms,
                rest_time_ms=self.rest_time_ms,
                start_time_ms=channel.start_time,
                end_time_ms=channel.end_time,
                center_volts=channel.center_volts,
                amplitude_volts=channel.amplitude_volts,
                frequency_hz=channel.frequency_hz
            )
            waveforms[name] = channel.waveform.generate_waveform(config)
        return waveforms

    def create_nidaqmx_task(self):
        if self.nidaqmx_task:
            self.nidaqmx_task.close()

        self.nidaqmx_task = nidaqmx.Task(self.name)

        if self.task_type == TaskType.AO:
            self._create_ao_channels()
        elif self.task_type == TaskType.DO:
            self._create_do_channels()
        elif self.task_type == TaskType.CO:
            self._create_co_channels()

        self._configure_timing()

    def _create_ao_channels(self):
        for channel in self.channels.values():
            self.nidaqmx_task.ao_channels.add_ao_voltage_chan(f"/{self.device_name}/{channel.port}")

    def _create_do_channels(self):
        for channel in self.channels.values():
            self.nidaqmx_task.do_channels.add_do_chan(f"/{self.device_name}/{channel.port}")

    def _create_co_channels(self):
        for channel in self.channels.values():
            self.nidaqmx_task.co_channels.add_co_pulse_chan_freq(
                f"/{self.device_name}/{channel.port}",
                freq=channel.frequency_hz,
                duty_cycle=0.5
            )

    def _configure_timing(self):
        samples_per_channel = int(self.sampling_frequency_hz * self.period_time_ms / 1000)
        self.nidaqmx_task.timing.cfg_samp_clk_timing(
            rate=self.sampling_frequency_hz,
            sample_mode=AcquisitionType.CONTINUOUS,
            samps_per_chan=samples_per_channel
        )

    def start(self):
        if self.nidaqmx_task:
            self.nidaqmx_task.start()

    def stop(self):
        if self.nidaqmx_task:
            self.nidaqmx_task.stop()

    def write_waveforms(self):
        if self.nidaqmx_task:
            waveforms = self.generate_waveforms()
            if self.task_type in [TaskType.AO, TaskType.DO]:
                self.nidaqmx_task.write(list(waveforms.values()), auto_start=True)

    def close(self):
        if self.nidaqmx_task:
            self.nidaqmx_task.close()
            self.nidaqmx_task = None

