from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from scipy import signal


# TODO Figure out if we need a start and end time for the waveform or just use a high/rise time to define the duty cycle
# Should the rest time always be at the end of the waveform or can it be in the beggining? or maybe split in two?

@dataclass
class DAQWaveformConfig:
    """
    Configuration class for DAQ waveform generation with improved voltage parameter handling.

    :param sampling_frequency_hz: The sampling frequency in Hz.
    :param period_time_ms: The period of the waveform in milliseconds.
    :param start_time_ms: The start time of the waveform in milliseconds.
    :param end_time_ms: The end time of the waveform in milliseconds.
    :param rest_time_ms: The rest time after the waveform in milliseconds.
    :param center_volts: The center voltage of the waveform.
    :param amplitude_volts: The peak-to-peak amplitude of the waveform.
    :param frequency_hz: The frequency for filtering the waveform in Hz.
    """
    sampling_frequency_hz: float
    period_time_ms: float
    start_time_ms: float
    end_time_ms: float
    rest_time_ms: float
    center_volts: float
    amplitude_volts: float
    frequency_hz: float

    def __post_init__(self):
        self.validate()

    def validate(self):
        """Validate the configuration parameters."""
        if self.start_time_ms < 0:
            raise ValueError("start_time_ms must be non-negative")
        if self.end_time_ms <= self.start_time_ms:
            raise ValueError("end_time_ms must be greater than start_time_ms")
        if self.end_time_ms > self.period_time_ms:
            raise ValueError("end_time_ms cannot exceed period_time_ms")
        if self.rest_time_ms < 0:
            raise ValueError("rest_time_ms must be non-negative")
        if self.amplitude_volts <= 0:
            raise ValueError("amplitude_volts must be positive")

    @property
    def min_volts(self) -> float:
        """Minimum voltage of the waveform."""
        return self.center_volts - self.amplitude_volts / 2

    @property
    def max_volts(self) -> float:
        """Maximum voltage of the waveform."""
        return self.center_volts + self.amplitude_volts / 2

    @property
    def total_cycle_time_ms(self) -> float:
        """Total time for one complete cycle including rest time."""
        return self.period_time_ms + self.rest_time_ms

    @property
    def duty_cycle(self) -> float:
        """Duty cycle of the waveform (for square waves)."""
        return (self.end_time_ms - self.start_time_ms) / self.period_time_ms

    @property
    def waveform_frequency_hz(self) -> float:
        """Actual frequency of the waveform."""
        return 1000 / self.period_time_ms

    def samples_per_cycle(self) -> int:
        """Number of samples in one complete cycle."""
        return int(self.total_cycle_time_ms * self.sampling_frequency_hz / 1000)

    def time_to_sample_index(self, time_ms: float) -> int:
        """Convert a time in milliseconds to a sample index."""
        return int(time_ms * self.sampling_frequency_hz / 1000)

    def get_period_sample_range(self) -> tuple[int, int]:
        """Get the sample range for one complete cycle of the waveform."""
        start = self.time_to_sample_index(0)
        end = self.time_to_sample_index(self.period_time_ms)
        return start, end

    def get_active_sample_range(self) -> tuple[int, int]:
        """Get the sample range for the active part of the waveform."""
        start = self.time_to_sample_index(self.start_time_ms)
        end = self.time_to_sample_index(self.end_time_ms)
        return start, end


def generate_square_waveform(config: DAQWaveformConfig) -> NDArray:
    """
    Generate a square waveform.

    :param config: The configuration for the waveform.
    :return: The generated square waveform as a numpy array.
    """
    samples = config.samples_per_cycle()
    start, end = config.get_active_sample_range()
    waveform = np.full(samples, config.min_volts)
    waveform[start:end] = config.max_volts
    return waveform


def generate_triangular_waveform(config: DAQWaveformConfig) -> NDArray:
    """
    Generate a triangular or sawtooth waveform based on the width parameter.

    :param config: The configuration for the waveform.
    :return: The generated waveform as a numpy array.
    """
    samples = config.samples_per_cycle()
    period_start, period_end = config.get_period_sample_range()
    period_samples = period_end - period_start
    active_start, active_end = config.get_active_sample_range()
    active_start = period_start
    # assert active_start == period_start, "Active period must start at the beginning of the cycle"
    active_samples = active_end - active_start
    assert period_samples <= samples, "Period time must be less than total cycle time"

    delay_samples = active_start - period_start
    rest_samples = samples - period_samples
    ramp_down_samples = period_samples - active_samples
    ramp_up_samples = period_samples - ramp_down_samples

    ramp_up_triangle = np.linspace(-1, 1, ramp_up_samples, endpoint=False)
    ramp_down_triangle = np.linspace(1, -1, ramp_down_samples, endpoint=False)
    triangle = np.concatenate((ramp_up_triangle, ramp_down_triangle))

    # Scale and shift the waveform to match the desired amplitude and center voltage
    waveform = config.center_volts + (config.amplitude_volts / 2) * triangle

    delay_section = np.full(delay_samples, 0)
    rest_section = np.full(rest_samples, 0)
    waveform = np.concatenate((delay_section, waveform, rest_section))

    return waveform


# TODO: Not needed since the triangular waveform is implemeted as a general case
def generate_triangle_waveform(config: DAQWaveformConfig) -> NDArray:
    """
    Generate a triangle waveform.

    :param config: The configuration for the waveform.
    :return: The generated triangle waveform as a numpy array.
    """
    return generate_triangular_waveform(config)


# TODO: Not needed since the sawtooth waveform is a special case of the triangular waveform
def generate_sawtooth_waveform(config: DAQWaveformConfig) -> NDArray:
    """
    Generate a sawtooth waveform.

    :param config: The configuration for the waveform.
    :return: The generated sawtooth waveform as a numpy array.
    """
    config = deepcopy(config)
    config.end_time_ms = config.period_time_ms * 0.85
    return generate_triangular_waveform(config)


def apply_low_pass_filter(waveform: NDArray, config: DAQWaveformConfig) -> NDArray:
    """
    Apply a low-pass filter to a waveform.

    :param waveform: The waveform to filter.
    :param config: The configuration for the waveform.
    :return: The filtered waveform as a numpy array.
    """
    # Apply a low-pass filter if requested
    n = 6  # Filter order
    sos = signal.bessel(n, config.frequency_hz / (config.sampling_frequency_hz / 2), output='sos')

    # Extend the waveform by repeating it once on each side
    extended_waveform = np.tile(waveform, 3)

    # Apply the filter
    filtered = signal.sosfiltfilt(sos, extended_waveform)

    # Return the central part of the filtered waveform
    return filtered[len(waveform):2 * len(waveform)]


class DAQWaveform(Enum):
    """
    Enumeration of available DAQ waveform types.
    """
    SQUARE = "square wave"
    TRIANGLE = "triangle wave"

    def generate_waveform(self, config: DAQWaveformConfig, filtered: Optional[bool] = None) -> NDArray:
        """
        Generate the waveform based on the enum type.

        :param config: The configuration for the waveform.
        :param filtered: Whether to apply a low-pass filter to the waveform.
        If None, the filter is applied to triangles.
        :return: The generated waveform as a numpy array.
        :rtype: NDArray
        """
        generators = {
            DAQWaveform.SQUARE: generate_square_waveform,
            DAQWaveform.TRIANGLE: generate_triangular_waveform
        }
        if filtered is None:
            filtered = self == DAQWaveform.TRIANGLE

        if not filtered:
            return generators[self](config)
        return apply_low_pass_filter(generators[self](config), config)


def plot_waveforms(waveforms: dict[str, NDArray], config: DAQWaveformConfig, num_cycles: int = 1,
                   save: bool = False, filename: str = None):
    """
    Plot multiple waveforms on the same graph with improved parameter highlighting.

    :param waveforms: Dictionary of waveforms to plot with their names as keys
    :param config: The configuration for the waveform
    :param num_cycles: Number of waveform cycles to plot (default is 1)
    :param save: Whether to save the plot to a file
    :param filename: The filename to save the plot (if save is True)
    """
    plt.figure(figsize=(15, 10))
    ax = plt.axes()

    total_time_ms = config.total_cycle_time_ms * num_cycles

    for i in range(num_cycles):
        start = i * config.total_cycle_time_ms
        period_start = start
        period_end = config.period_time_ms + period_start
        period_center = period_start + (period_end - period_start) / 2

        rest_start = config.period_time_ms + start
        rest_end = config.rest_time_ms + rest_start
        rest_center = rest_start + (rest_end - rest_start) / 2

        # plot yellow background for period times
        ax.axvspan(period_start, period_end, facecolor='yellow', alpha=0.05, edgecolor='none')
        # add text labels for time periods
        ax.text(rest_center, config.min_volts - 0.1 * config.amplitude_volts,
                f'Rest: {config.rest_time_ms:.2f} ms', ha='center', va='top', fontsize=9)
        ax.text(period_center, config.min_volts - 0.1 * config.amplitude_volts,
                f'Period: {config.period_time_ms:.2f} ms', ha='center', va='top', fontsize=9)

    colors = ['blue', 'green', 'red', 'purple', 'cyan', 'orange']
    color_idx = 0
    for waveform_name, single_waveform in waveforms.items():
        waveform = np.tile(single_waveform, num_cycles)
        time_ms = np.linspace(0, total_time_ms, len(waveform))
        plt.plot(time_ms, waveform, label=waveform_name, color=colors[color_idx])
        color_idx = (color_idx + 1) % len(colors)

    # Highlight config parameters
    ax.axhline(y=config.center_volts, color='purple', linestyle='--', alpha=0.7, label='Center Voltage')
    ax.axhline(y=config.max_volts, color='orange', linestyle=':', alpha=0.7, label='Max Voltage')
    ax.axhline(y=config.min_volts, color='cyan', linestyle=':', alpha=0.7, label='Min Voltage')

    plt.title(f"Combined Waveforms ({num_cycles} cycles)")
    plt.xlabel("Time (ms)")
    plt.ylabel("Voltage (V)")

    y_range = config.amplitude_volts
    y_padding = 0.3 * y_range
    ax.set_ylim(config.min_volts - y_padding, config.max_volts + y_padding)
    ax.set_xlim(0, total_time_ms)

    ax.spines[['right', 'top']].set_visible(False)
    plt.legend()
    plt.grid(True, which='both', linestyle=':', alpha=0.5)

    # Add annotations for config parameters
    plt.annotate(f"Duty Cycle: {config.duty_cycle:.2%}", xy=(0.02, 0.96), xycoords='axes fraction',
                 verticalalignment='top', fontsize=10)
    plt.annotate(f"Frequency: {config.waveform_frequency_hz:.2f} Hz", xy=(0.02, 0.93), xycoords='axes fraction',
                 verticalalignment='top', fontsize=10)
    plt.annotate(f"Start Time: {config.start_time_ms:.2f} ms", xy=(0.02, 0.90), xycoords='axes fraction',
                 verticalalignment='top', fontsize=10)
    plt.annotate(f"End Time: {config.end_time_ms:.2f} ms", xy=(0.02, 0.87), xycoords='axes fraction',
                 verticalalignment='top', fontsize=10)

    if save:
        if filename is None:
            filename = f"combined_waveforms_{num_cycles}cycles.pdf"
        plt.savefig(filename, bbox_inches='tight')
        print(f"Combined waveform plot saved as {filename}")
    else:
        plt.show()
