from abc import abstractmethod
from enum import StrEnum

from matplotlib import pyplot as plt
import numpy as np
from scipy import signal

from voxel.core.utils.descriptors.new import deliminated_property
from voxel.core.utils.log_config import get_component_logger

type Waveform = np.ndarray[float]


class DAQPortType(StrEnum):
    """Available DAQ port types."""

    ANALOG_OUTPUT = "ao"
    DIGITAL_OUTPUT = "do"


type DAQPortIds = dict[DAQPortType, list[str]]


class VoxelDAQ:

    def __init__(self, name: str) -> None:
        self.name = name
        self.log = get_component_logger(self)
        self.tasks: dict[str, "VoxelDAQTask"] = {}

    @property
    @abstractmethod
    def ao_ports(self) -> list[str]:
        pass

    @abstractmethod
    def is_port_available(self, port_id: str, port_type: DAQPortType) -> bool:
        pass

    @abstractmethod
    def register_task(self, task: "VoxelDAQTask") -> None:
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists.")


class DAQTaskTriggerMode(StrEnum):
    OFF = "off"
    ON = "on"


class DAQTaskTriggerEdge(StrEnum):
    RISING = "rising"
    FALLING = "falling"


class DAQTaskSampleMode(StrEnum):
    CONTINUOUS = "continuous"
    FINITE = "finite"


class VoxelDAQTask:
    """A collection of DAQ ports with shared timing parameters. A task can be started and stopped.
    :param name: The name of the task.
    :param daq: The DAQ device the task is associated with.
    :param sampling_frequency_hz: The sampling frequency of the task in Hz.
    :param period_time_ms: The period of the task in ms.
    """

    def __init__(self, name: str, daq: VoxelDAQ, sampling_frequency_hz: float, period_ms: float) -> None:
        self.name = name
        self.log = get_component_logger(self)
        self.daq = daq
        self._sampling_frequency_hz = sampling_frequency_hz
        self._period_ms = period_ms
        self.ports: dict[str, "DAQPort"] = {}
        self.daq.register_task(self)

    @abstractmethod
    def add_port(self, port_id: str, port_type: DAQPortType) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @property
    @abstractmethod
    def is_running(self) -> bool:
        pass

    @abstractmethod
    def write_waveforms(self) -> None:
        pass

    @property
    def frequency(self) -> float:
        """The frequency of the task waveforms in Hz."""
        return 1000 / self.period_ms

    @property
    def samples_per_period(self) -> int:
        """The number of samples per period."""
        return int(self.sampling_frequency_hz * self.period_ms / 1000)

    @deliminated_property(
        minimum=0,
        maximum=1e6,
    )
    def period_ms(self) -> float:
        return self._period_ms

    @period_ms.setter
    def period_ms(self, value: float) -> None:
        self._period_ms = value
        self._update_ports()

    @deliminated_property(
        minimum=0,
        maximum=1e6,
    )
    def sampling_frequency_hz(self) -> float:
        return self._sampling_frequency_hz

    @sampling_frequency_hz.setter
    def sampling_frequency_hz(self, value: float) -> None:
        self._sampling_frequency_hz = value
        self._update_ports()

    def _update_ports(self) -> None:
        for port in self.ports.values():
            port.regenerate_waveform()

    def plot_waveforms(self, periods: int = 2) -> plt.Figure:
        period_time_ms = self.period_ms
        colors = plt.get_cmap("rainbow")(np.linspace(0, 1, len(self.ports)))
        fig, ax = plt.subplots()

        # plot period and rest time backgrounds
        for i in range(periods):
            ax.axvspan(i * period_time_ms, (i + 1) * period_time_ms, facecolor="yellow", alpha=0.05, edgecolor="none")

        # plot waveforms for each port
        for port in self.ports.values():
            port.plot_waveform(ax, color=colors.pop(0), periods=periods)

        ax.set_xlim(0, periods * self.period_ms)
        y_max = max(port.peak_volts for port in self.ports.values())
        y_min = min(port.base_volts for port in self.ports.values())
        y_padding = 0.1 * (y_max - y_min)
        ax.set_ylim(y_min - y_padding, y_max + y_padding)

        ax.set_title(f"{self.name} task Waveforms (periods={periods})")
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Voltage (V)")
        ax.legend()

        info = "\n".join(
            [
                f"Sampling Frequency: {self.sampling_frequency_hz} Hz",
                f"Period Time: {self.period_ms} ms",
                f"Waveform Frequency: {self.frequency} Hz",
            ]
        )
        ax.text(
            0.02,
            0.98,
            info,
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.5),
        )

        return fig


class DAQPort:
    """
    A DAQ port.
    :param name: The name of the port.
    :param task: The task the port is associated with.
    :param port_type: The type of the port.
    :param port_id: The ID of the port.
    :param center_volts: The center voltage of the waveform.
    :param amplitude_volts: The amplitude of the waveform.
    :param cutoff_frequency_hz: The cutoff frequency of the waveform in Hz.
    :param start: Fraction of the period when the waveform starts rising.
    :param high: Fraction of the period when the waveform peaks.
    :param fall: Fraction of the period when the waveform starts falling.
    :param end: Fraction of the period when the active section ends
    :param low_pass_filter: Whether to apply a low pass filter to the waveform.
    """

    def __init__(
        self,
        name: str,
        task: VoxelDAQTask,
        port_type: DAQPortType,
        port_id: str,
        max_volts: float,
        min_volts: float,
        center_volts: float,
        amplitude_volts: float,
        cutoff_frequency_hz: float,
        low_pass_filter: bool = False,
        start: float = 0.0,
        high: float = 0,
        fall: float = 0,
        end: float = 0.5,
    ) -> None:
        self.name = name
        self.log = get_component_logger(self)
        self.task = task
        self.port_type = port_type
        self.port_id = port_id
        self.max_volts = max_volts
        self.min_volts = min_volts
        self._center_volts = center_volts
        self._amplitude_volts = amplitude_volts
        self._cutoff_frequency_hz = cutoff_frequency_hz
        self._low_pass_filter = low_pass_filter
        self._start = start
        self._end = end
        self._high = high
        self._fall = fall
        self._waveform: Waveform = self._generate_waveform()

    @deliminated_property(
        minimum=lambda self: self.min_device_volts,
        maximum=lambda self: self.max_device_volts,
    )
    def center_volts(self) -> float:
        return self._center_volts

    @center_volts.setter
    def center_volts(self, value: float) -> None:
        self._center_volts = value
        self.amplitude_volts = self.amplitude_volts

    @deliminated_property(
        minimum=0,
        maximum=lambda self: self._get_max_amplitude(),
    )
    def amplitude_volts(self) -> float:
        return self._amplitude_volts

    @amplitude_volts.setter
    def amplitude_volts(self, value: float) -> None:
        self._amplitude_volts = value

    def _get_max_amplitude(self) -> float:
        return min((self.max_volts - self.center_volts), (self.center_volts - self.min_volts))

    @deliminated_property(
        minimum=0,
        maximum=lambda self: self.task.timing.sampling_frequency_hz / 2,
    )
    def cut_off_frequency_hz(self) -> float:
        return self._cut_off_frequency_hz

    @cut_off_frequency_hz.setter
    def cut_off_frequency_hz(self, value: float) -> None:
        self._cut_off_frequency_hz = value

    @property
    def low_pass_filter(self) -> bool:
        return self._low_pass_filter

    @low_pass_filter.setter
    def low_pass_filter(self, value: bool) -> None:
        self._low_pass_filter = value

    @deliminated_property(
        minimum=0,
        maximum=1,
    )
    def start(self) -> float:
        return self._start

    @start.setter
    def start(self, value: float) -> None:
        self._start = value
        self.high = self.high

    @deliminated_property(
        minimum=lambda self: self.start,
        maximum=lambda self: self.fall,
    )
    def high(self) -> float:
        return self._high

    @high.setter
    def high(self, value: float) -> None:
        self._high = value
        self.fall = self.fall

    @deliminated_property(
        minimum=lambda self: self.high,
        maximum=lambda self: self.end,
    )
    def fall(self) -> float:
        return self._fall

    @fall.setter
    def fall(self, value: float) -> None:
        self._fall = value
        self.end = self.end

    @deliminated_property(
        minimum=lambda self: self.fall,
        maximum=1,
    )
    def end(self) -> float:
        return self._end

    @end.setter
    def end(self, value: float) -> None:
        self._end = value
        self.regenerate_waveform()

    @property
    def peak_volts(self) -> float:
        return self.center_volts + self.amplitude_volts

    @property
    def base_volts(self) -> float:
        return self.center_volts - self.amplitude_volts

    @property
    def waveform(self) -> Waveform:
        """The waveform of the port.
        Note: The waveform is regenerated when the port is created and
        when the start, high, fall, or end properties are set.
        """
        return self._waveform

    def regenerate_waveform(self) -> None:
        self._waveform = self._generate_waveform()

    def _generate_waveform(self) -> Waveform:
        samples = self.task.samples_per_period
        waveform = np.zeros(samples)
        start = int(samples * self.start)
        high = int(samples * self.high)
        fall = int(samples * self.fall)
        end = int(samples * self.end)
        waveform[:start] = self.base_volts
        waveform[end:] = self.base_volts
        if self.high > self.start:
            waveform[start:high] = np.linspace(self.base_volts, self.peak_volts, high - start)
        waveform[high:fall] = self.peak_volts
        if self.fall < self.end:
            waveform[fall:end] = np.linspace(self.peak_volts, self.base_volts, end - fall)
        if not self.low_pass_filter:
            return waveform
        return self._apply_low_pass_filter(waveform, self.cut_off_frequency_hz, self.task.timing.sampling_frequency_hz)

    @staticmethod
    def _apply_low_pass_filter(
        waveform: Waveform, cutoff_frequency_hz: float, sampling_frequency_hz: float
    ) -> Waveform:
        if cutoff_frequency_hz == 0:
            return waveform
        samples = len(waveform)
        order = 6
        nyquist_frequency = sampling_frequency_hz / 2
        normalized_cutoff_frequency = cutoff_frequency_hz / nyquist_frequency
        sos = signal.bessel(order, normalized_cutoff_frequency, output="sos")
        extended_waveform = np.tile(waveform, 3)
        filtered_waveform = signal.sosfiltfilt(sos, extended_waveform)
        middle_range_end = samples * 2
        return filtered_waveform[samples:middle_range_end]

    def plot_waveform(self, ax: plt.Axes, color, periods: int = 2) -> plt.Axes:
        # Plot period and rest time backgrounds
        period_time_ms = self.task.period_time_ms
        for i in range(periods):
            ax.axvspan(i * period_time_ms, (i + 1) * period_time_ms, facecolor="yellow", alpha=0.05, edgecolor="none")

        # Plot waveform
        full_waveform = np.tile(self.waveform, periods)
        time = np.linspace(0, periods * period_time_ms, len(full_waveform))
        ax.plot(time, full_waveform, color=color, label=self.name)
        ax.axhline(self.center_volts, color="gray", linestyle="--", alpha=0.5)
        return ax
