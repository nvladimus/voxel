"""
Module for defining the DAQ channel configuration.
Contains:
    - DAQWaveform: Enumeration of available DAQ waveform_type types.
    - DAQTaskTiming: Configuration for the timing of the parent task. Channels follow the timing of their parent task.
    - DAQTaskChannel: Configuration for a single channel of a DAQ task.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy import signal


class DAQWaveform(StrEnum):
    """
    Enumeration of available DAQ waveform_type types.
    """
    SQUARE = "square wave"
    TRIANGLE = "triangle wave"


@dataclass
class DAQTaskTiming:
    sampling_frequency_hz: float
    period_time_ms: float
    rest_time_ms: float

    @property
    def waveform_frequency_hz(self) -> float:
        """Actual frequency of the waveform_type."""
        return 1000 / self.period_time_ms

    @property
    def total_cycle_time_ms(self) -> float:
        """Total time for one complete cycle including rest time."""
        return self.period_time_ms + self.rest_time_ms

    def samples_per_cycle(self) -> int:
        """Number of samples in one complete cycle."""
        return int(self.total_cycle_time_ms * self.sampling_frequency_hz / 1000)

    def time_to_sample_index(self, time_ms: float) -> int:
        """Convert time in milliseconds to sample index."""
        return int(time_ms * self.sampling_frequency_hz / 1000)

    def get_period_sample_range(self) -> Tuple[int, int]:
        """Get the sample range for one complete cycle."""
        return self.time_to_sample_index(0), self.time_to_sample_index(self.period_time_ms)


# TODO Figure out if we need a start and end time for the waveform_type or just use a high/rise time to define the duty cycle
# Should the rest time always be at the end of the waveform_type or can it be in the beggining? or maybe split in two?
@dataclass
class DAQTaskChannel:
    name: str
    port: str
    waveform_type: DAQWaveform
    center_volts: float
    amplitude_volts: float
    start_time_ms: float
    end_time_ms: float
    cut_off_frequency_hz: float
    _timing: Optional[DAQTaskTiming] = None

    def __post_init__(self):
        self._timing = None  # no timing by default
        self.validate()

    def set_timing(self, timing: DAQTaskTiming):
        self._timing = timing

    @property
    def min_volts(self) -> float:
        """Minimum voltage of the waveform_type."""
        return self.center_volts - self.amplitude_volts / 2

    @property
    def max_volts(self) -> float:
        """Maximum voltage of the waveform_type."""
        return self.center_volts + self.amplitude_volts / 2

    def validate(self):
        """Validate the configuration parameters."""
        if self.cut_off_frequency_hz <= 0:
            raise ValueError(f"Frequency must be greater than 0. Got {self.cut_off_frequency_hz}")
        if self.start_time_ms < 0:
            raise ValueError("start_time_ms must be non-negative")
        if self.end_time_ms <= self.start_time_ms:
            raise ValueError("end_time_ms must be greater than start_time_ms")
        # if self.end_time_ms > self.period_time_ms:
        #     raise ValueError("end_time_ms cannot exceed period_time_ms")
        # if self.rest_time_ms < 0:
        #     raise ValueError("rest_time_ms must be non-negative")
        if self.amplitude_volts <= 0:
            raise ValueError("amplitude_volts must be positive")

    def generate_waveform(self, timing: 'DAQTaskTiming', filtered: Optional[bool] = None) -> NDArray:
        """
        Generate the waveform_type based on the enum type.

        :param timing: Timing configuration for the task.
        :param filtered: Whether to apply a low-pass filter to the waveform_type.
        If None, the filter is applied to triangles.
        :return: The generated waveform_type as a numpy array.
        :rtype: NDArray
        """
        generators = {
            DAQWaveform.SQUARE: self._generate_square_waveform,
            DAQWaveform.TRIANGLE: self._generate_triangular_waveform
        }
        if filtered is None:
            filtered = self == DAQWaveform.TRIANGLE

        if not filtered:
            return generators[self.waveform_type](timing)
        return self._apply_low_pass_filter(
            waveform=generators[self.waveform_type](timing),
            sampling_frequency_hz=timing.sampling_frequency_hz,
            cut_off_frequency_hz=self.cut_off_frequency_hz
        )

    def _generate_square_waveform(self, timing: DAQTaskTiming) -> NDArray:
        samples = timing.samples_per_cycle()
        start = timing.time_to_sample_index(self.start_time_ms)
        end = timing.time_to_sample_index(self.end_time_ms)
        waveform = np.full(samples, self.min_volts)
        waveform[start:end] = self.max_volts
        return waveform

    def _generate_triangular_waveform(self, timing: DAQTaskTiming) -> NDArray:
        samples = timing.samples_per_cycle()
        period_start, period_end = timing.get_period_sample_range()
        # TODO: Figure out appropriate behavior. for now, adjust the start to the beginning of the period
        # active_start = timing.time_to_sample_index(self.start_time_ms)
        active_start = period_start
        active_end = timing.time_to_sample_index(self.end_time_ms)

        active_samples = active_end - active_start
        period_samples = period_end - period_start

        assert period_samples <= samples, "Period time must be less than total cycle time"

        delay_samples = active_start - period_start
        rest_samples = samples - period_samples
        ramp_down_samples = period_samples - active_samples
        ramp_up_samples = period_samples - ramp_down_samples

        ramp_up_triangle = np.linspace(-1, 1, ramp_up_samples, endpoint=False)
        ramp_down_triangle = np.linspace(1, -1, ramp_down_samples, endpoint=False)
        triangle = np.concatenate((ramp_up_triangle, ramp_down_triangle))

        # Scale and shift the waveform_type to match the desired amplitude and center voltage
        waveform = self.center_volts + (self.amplitude_volts / 2) * triangle

        delay_section = np.full(delay_samples, self.min_volts)
        rest_section = np.full(rest_samples, self.min_volts)
        waveform = np.concatenate((delay_section, waveform, rest_section))

        return waveform

    @staticmethod
    def _apply_low_pass_filter(waveform: NDArray, cut_off_frequency_hz, sampling_frequency_hz) -> NDArray:
        """
        Apply a low-pass filter to a waveform_type.

        :param waveform: The waveform_type to filter.
        :param cut_off_frequency_hz: The cut-off frequency for the filter in Hz.
        :param sampling_frequency_hz: The sampling frequency of the waveform_type in Hz.
        :return: The filtered waveform_type as a numpy array.
        """
        # Apply a low-pass filter if requested
        n = 6  # Filter order
        sos = signal.bessel(n, cut_off_frequency_hz / (sampling_frequency_hz / 2), output='sos')

        # Extend the waveform_type by repeating it once on each side
        extended_waveform = np.tile(waveform, 3)

        # Apply the filter
        filtered = signal.sosfiltfilt(sos, extended_waveform)

        # Return the central part of the filtered waveform_type
        return filtered[len(waveform):2 * len(waveform)]
