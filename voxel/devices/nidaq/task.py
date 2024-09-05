from dataclasses import dataclass, field
from enum import StrEnum
from typing import Dict, Optional, TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from voxel.devices.nidaq.channel import DAQTaskChannel, DAQTaskTiming, DAQWaveform

if TYPE_CHECKING:
    from voxel.devices.nidaq.base import HardwareTask


class DAQTaskType(StrEnum):
    AO = "ao"
    DO = "do"
    CO = "co"


class DAQTaskTriggerMode(StrEnum):
    OFF = "off"
    ON = "on"


class DAQTaskTriggerEdge(StrEnum):
    RISING = "rising"
    FALLING = "falling"


class DAQTaskSampleMode(StrEnum):
    CONTINUOUS = "continuous"
    FINITE = "finite"


@dataclass
class DAQTask:
    name: str
    task_type: DAQTaskType
    sampling_frequency_hz: float
    period_time_ms: float
    rest_time_ms: float
    daq: 'VoxelDAQ | VoxelNIDAQ'
    channels: Dict[str, DAQTaskChannel] = field(default_factory=dict)
    hardware_task: Optional['HardwareTask'] = None
    sample_mode: DAQTaskSampleMode = DAQTaskSampleMode.CONTINUOUS
    trigger_mode: DAQTaskTriggerMode = DAQTaskTriggerMode.OFF
    trigger_edge: DAQTaskTriggerEdge = DAQTaskTriggerEdge.RISING
    trigger_source: Optional[str] = None
    retriggerable: bool = False

    @property
    def timing(self) -> DAQTaskTiming:
        return DAQTaskTiming(
            sampling_frequency_hz=self.sampling_frequency_hz,
            period_time_ms=self.period_time_ms,
            rest_time_ms=self.rest_time_ms
        )

    @property
    def waveform_frequency_hz(self) -> float:
        """Actual frequency of the waveform_type."""
        return 1000 / self.period_time_ms

    @property
    def total_cycle_time_ms(self) -> float:
        """Total time for one complete cycle including rest time."""
        return self.period_time_ms + self.rest_time_ms

    def get_duty_cycle(self, channel_name: str) -> float:
        """Duty cycle of the waveform_type (for square waves)."""
        channel = self.channels[channel_name]
        return (channel.end_time_ms - channel.start_time_ms) / self.period_time_ms

    def add_channel(self, channel: DAQTaskChannel):
        if channel.name in self.channels:
            raise ValueError(f"Channel with name '{channel.name}' already exists in this task")

        # Check if the channel port is valid
        match self.task_type:
            case DAQTaskType.AO:
                if not self.daq.is_valid_port(channel.port, DAQTaskType.AO):
                    raise ValueError(f"Invalid port: '{channel.port}' Must be one of {self.daq.ao_physical_chans}")
            case DAQTaskType.DO:
                if not self.daq.is_valid_port(channel.port, DAQTaskType.DO):
                    raise ValueError(f"Invalid port: '{channel.port}' Must be one of {self.daq.do_physical_chans}")
            case DAQTaskType.CO:
                if not self.daq.is_valid_port(channel.port, DAQTaskType.CO):
                    raise ValueError(f"Invalid port: '{channel.port}' Must be one of {self.daq.co_physical_chans}")

        # check the waveform_type is valid for the task type
        if self.task_type == DAQTaskType.CO and channel.waveform_type != DAQWaveform.SQUARE:
            channel.waveform_type = DAQWaveform.SQUARE
            self.daq.log.warning(f"Channel '{channel.name}' waveform_type changed to SQUARE for CO task")

        # channel volts must fit within the range of the device
        if channel.max_volts > self.daq.ao_voltage_range[0] or channel.min_volts < self.daq.ao_voltage_range[1]:
            raise ValueError(f"Channel '{channel.name}' exceeds the voltage range of the device. "
                             f"Range: {self.daq.ao_voltage_range}")

        self.channels[channel.name] = channel
        self._update_task()

    def remove_channel(self, channel_name: str):
        self.channels.pop(channel_name, None)
        self._update_task()

    def get_channel(self, channel_name: str) -> Optional[DAQTaskChannel]:
        return self.channels.get(channel_name)

    def _update_task(self):
        self.daq.register_task(self)

    def generate_waveforms(self) -> Dict[str, NDArray]:
        waveforms = {}
        for name, channel in self.channels.items():
            waveforms[name] = channel.generate_waveform(self.timing)
        return waveforms

    def write_waveforms(self):
        self.daq.write_task_waveforms(self.name)

    def plot_waveforms(self, num_cycles: int = 1, save: bool = False, filename: str = None):
        waveforms = self.generate_waveforms()

        fig, ax = plt.subplots(figsize=(15, 10))

        total_time_ms = self.timing.total_cycle_time_ms * num_cycles

        # Plot period and rest time backgrounds
        for i in range(num_cycles):
            start = i * self.timing.total_cycle_time_ms
            period_end = start + self.timing.period_time_ms
            ax.axvspan(start, period_end, facecolor='yellow', alpha=0.05, edgecolor='none')

        # Plot waveforms
        colors = plt.cm.rainbow(np.linspace(0, 1, len(waveforms)))
        y_range = 0, 0
        for (name, waveform), color in zip(waveforms.items(), colors):
            channel = self.channels[name]
            y_range = min(y_range[0], channel.min_volts), max(y_range[1], channel.max_volts)
            full_waveform = np.tile(waveform, num_cycles)
            time_ms = np.linspace(0, total_time_ms, len(full_waveform))
            ax.plot(time_ms, full_waveform, label=name, color=color)

            # Plot channel-specific lines and annotations
            ax.axhline(y=channel.center_volts, color=color, linestyle='--', alpha=0.5)
            ax.axhline(y=channel.max_volts, color=color, linestyle=':', alpha=0.5)
            ax.axhline(y=channel.min_volts, color=color, linestyle=':', alpha=0.5)

        ax.set_title(f"{self.name} task Waveforms ({num_cycles} cycles)")
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Voltage (V)")

        ax.set_xlim(0, total_time_ms)
        ax.spines[['right', 'top']].set_visible(False)
        ax.legend()
        ax.grid(True, which='both', linestyle=':', alpha=0.5)

        y_padding = 0.15 * (y_range[1] - y_range[0])
        ax.set_ylim(y_range[0] - 0.1, y_range[1] + y_padding)
        # Create a text box for task-level annotations
        textstr = '\n'.join((
            f"Sampling Frequency: {self.sampling_frequency_hz:.2f} Hz",
            f"Waveform Frequency: {self.waveform_frequency_hz:.2f} Hz",
            f"Period Time: {self.period_time_ms:.2f} ms",
            f"Rest Time: {self.rest_time_ms:.2f} ms"))

        # Place a white box with task information in upper left
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)

        plt.tight_layout()

        if save:
            if filename is None:
                filename = f"{self.name}_waveforms_{num_cycles}cycles.pdf"
            plt.savefig(filename, bbox_inches='tight')
            print(f"Waveform plot saved as {filename}")
        else:
            plt.show()

    def start(self):
        self.daq.start_task(self.name)

    def stop(self):
        self.daq.stop_task(self.name)

    def close(self):
        self.daq.close_task(self.name)

    # def plot_waveforms(self, num_cycles: int = 1):
    #     waveforms = self.generate_waveforms()
    #     plt_channel = next(iter(self.channels.values()))
    #     self._plot_waveforms(waveforms, self.timing, plt_channel, num_cycles)

    @staticmethod
    def _plot_waveforms(
            waveforms: dict[str, NDArray],
            timing: DAQTaskTiming,
            channel: DAQTaskChannel,
            num_cycles: int = 1,
            save: bool = False, filename: str = None):
        """
        Plot multiple waveforms on the same graph with improved parameter highlighting.

        :param waveforms: Dictionary of waveforms to plot with their names as keys
        :param timing: The timing configuration for the waveforms
        :param channel: The channel configuration for the waveforms
        :param num_cycles: Number of waveform_type cycles to plot (default is 1)
        :param save: Whether to save the plot to a file
        :param filename: The filename to save the plot (if save is True)
        """
        plt.figure(figsize=(15, 10))
        ax = plt.axes()

        total_time_ms = timing.total_cycle_time_ms * num_cycles

        for i in range(num_cycles):
            start = i * timing.total_cycle_time_ms
            period_start = start
            period_end = timing.period_time_ms + period_start
            period_center = period_start + (period_end - period_start) / 2

            rest_start = timing.period_time_ms + start
            rest_end = timing.rest_time_ms + rest_start
            rest_center = rest_start + (rest_end - rest_start) / 2

            # plot yellow background for period times
            ax.axvspan(period_start, period_end, facecolor='yellow', alpha=0.05, edgecolor='none')
            # add text labels for time periods
            ax.text(rest_center, channel.min_volts - 0.1 * channel.amplitude_volts,
                    f'Rest: {timing.rest_time_ms:.2f} ms', ha='center', va='top', fontsize=9)
            ax.text(period_center, channel.min_volts - 0.1 * channel.amplitude_volts,
                    f'Period: {timing.period_time_ms:.2f} ms', ha='center', va='top', fontsize=9)

        colors = ['blue', 'green', 'red', 'purple', 'cyan', 'orange']
        color_idx = 0
        for waveform_name, single_waveform in waveforms.items():
            waveform = np.tile(single_waveform, num_cycles)
            time_ms = np.linspace(0, total_time_ms, len(waveform))
            plt.plot(time_ms, waveform, label=waveform_name, color=colors[color_idx])
            color_idx = (color_idx + 1) % len(colors)

        # Highlight config parameters
        ax.axhline(y=channel.center_volts, color='purple', linestyle='--', alpha=0.7, label='Center Voltage')
        ax.axhline(y=channel.max_volts, color='orange', linestyle=':', alpha=0.7, label='Max Voltage')
        ax.axhline(y=channel.min_volts, color='cyan', linestyle=':', alpha=0.7, label='Min Voltage')

        plt.title(f"Combined Waveforms ({num_cycles} cycles)")
        plt.xlabel("Time (ms)")
        plt.ylabel("Voltage (V)")

        y_range = channel.amplitude_volts
        y_padding = 0.3 * y_range
        ax.set_ylim(channel.min_volts - y_padding, channel.max_volts + y_padding)
        ax.set_xlim(0, total_time_ms)

        ax.spines[['right', 'top']].set_visible(False)
        plt.legend()
        plt.grid(True, which='both', linestyle=':', alpha=0.5)

        duty_cycle = (channel.end_time_ms - channel.start_time_ms) / timing.period_time_ms

        # Add annotations for config parameters
        plt.annotate(f"Duty Cycle: {duty_cycle:.2%}", xy=(0.02, 0.96), xycoords='axes fraction',
                     verticalalignment='top', fontsize=10)
        plt.annotate(f"Frequency: {timing.waveform_frequency_hz:.2f} Hz", xy=(0.02, 0.93), xycoords='axes fraction',
                     verticalalignment='top', fontsize=10)
        plt.annotate(f"Start Time: {channel.start_time_ms:.2f} ms", xy=(0.02, 0.90), xycoords='axes fraction',
                     verticalalignment='top', fontsize=10)
        plt.annotate(f"End Time: {channel.end_time_ms:.2f} ms", xy=(0.02, 0.87), xycoords='axes fraction',
                     verticalalignment='top', fontsize=10)

        if save:
            if filename is None:
                filename = f"combined_waveforms_{num_cycles}cycles.pdf"
            plt.savefig(filename, bbox_inches='tight')
            print(f"Combined waveform_type plot saved as {filename}")
        else:
            plt.show()
