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

from voxel.utils.descriptors.deliminated_property import deliminated_property
from voxel.utils.descriptors.enumerated_property import enumerated_property
from voxel.instrument.device import VoxelDevice


class DAQWaveform(StrEnum):
    """
    Enumeration of available DAQ waveform_type types.
    """
    SQUARE = "square"
    TRIANGLE = "triangle"


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


class DAQTaskChannel(VoxelDevice):
    """
    Configuration for a single channel of a DAQ task.
    :param name: Name of the channel.
    :param port: Physical port of the channel.
    :param waveform_type: Type of waveform_type to generate.
    :param center_volts: Center voltage of the waveform_type.
    :param amplitude_volts: Amplitude of the waveform_type.
    :param max_device_volts: Maximum voltage allowed by the device.
    :param min_device_volts: Minimum voltage allowed by the device.
    :param task_timing: Timing configuration for the task.
    :param cutoff_freq_hz: Cut-off frequency for the low-pass filter.
    :param start_time_ms: Start time of the waveform_type in milliseconds.
    :param end_time_ms: End time of the waveform_type in milliseconds.
    :param peak_point: Peak point of the waveform_type as a fraction of the period. Defaults to None.
    Note: For a square waveform_type, the start and end times represent the active portion of the waveform_type.
    Note: For triangular waveform_type, the start time is adjusted to the beginning of the period.
            The end time represents the point where the waveform peaks.
    Note: For triangular waveform_type, the peak point is the fraction of the period time where the waveform_type peaks.
        Start and end times are ignored if peak point is provided.
    """

    def __init__(self, name: str, port: str, waveform_type: DAQWaveform,
                 center_volts: float, amplitude_volts: float, max_device_volts: float, min_device_volts: float,
                 task_timing: DAQTaskTiming, cutoff_freq_hz: float, start_time_ms: Optional[float] = None,
                 end_time_ms: Optional[float] = None, peak_point: Optional[float] = None):
        super().__init__(name=name)
        self.waveform_type = waveform_type
        self.max_device_volts = max_device_volts
        self.min_device_volts = min_device_volts
        self.center_volts = center_volts
        self.amplitude_volts = amplitude_volts
        self.timing: DAQTaskTiming = task_timing
        if not start_time_ms and not end_time_ms and not peak_point:
            start_time_ms = 0
            end_time_ms = self.timing.period_time_ms // 2
        elif peak_point and waveform_type == DAQWaveform.TRIANGLE:
            start_time_ms = 0
            end_time_ms = self.timing.period_time_ms * peak_point
        else:
            start_time_ms = 0 if not start_time_ms or start_time_ms < 0 else start_time_ms
            start_time_ms = self.timing.period_time_ms if start_time_ms > self.timing.period_time_ms else start_time_ms
            end_time_ms = self.timing.period_time_ms if end_time_ms > self.timing.period_time_ms else end_time_ms
            end_time_ms = start_time_ms if not end_time_ms or end_time_ms < start_time_ms else end_time_ms
        self._start_time_ms = start_time_ms
        self._end_time_ms = end_time_ms
        self.cut_off_frequency_hz = cutoff_freq_hz
        self.port = port

    @enumerated_property(DAQWaveform, lambda self: [w for w in DAQWaveform])
    def waveform_type(self) -> DAQWaveform:
        return self._waveform_type

    @waveform_type.setter
    def waveform_type(self, value: DAQWaveform):
        self._waveform_type = value

    @deliminated_property(
        minimum=0,
        maximum=lambda self: self._get_max_amplitude(),
        unit="V",
    )
    def amplitude_volts(self) -> float:
        return self._amplitude_volts

    @amplitude_volts.setter
    def amplitude_volts(self, value: float):
        self._amplitude_volts = value

    def _get_max_amplitude(self):
        return min((self.max_device_volts - self.center_volts), (self.center_volts - self.min_device_volts))

    @deliminated_property(
        minimum=lambda self: self.min_device_volts,
        maximum=lambda self: self.max_device_volts,
    )
    def center_volts(self) -> float:
        return self._center_volts

    @center_volts.setter
    def center_volts(self, value: float):
        self._center_volts = value

    @deliminated_property(
        minimum=0,
        maximum=lambda self: self.end_time_ms,
        unit="ms",
    )
    def start_time_ms(self) -> float:
        return self._start_time_ms

    @start_time_ms.setter
    def start_time_ms(self, value: float):
        self._start_time_ms = value

    @deliminated_property(
        minimum=lambda self: self.start_time_ms,
        maximum=lambda self: self.timing.period_time_ms,
        unit="ms",
    )
    def end_time_ms(self) -> float:
        return self._end_time_ms

    @end_time_ms.setter
    def end_time_ms(self, value: float):
        self._end_time_ms = value

    @deliminated_property(
        minimum=0,
        maximum=lambda self: self.timing.sampling_frequency_hz / 2,
        unit="Hz",
    )
    def cut_off_frequency_hz(self) -> float:
        return self._cut_off_frequency_hz

    @cut_off_frequency_hz.setter
    def cut_off_frequency_hz(self, value: float):
        self._cut_off_frequency_hz = value

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
        waveform = np.full(samples, self.center_volts - self.amplitude_volts)
        waveform[start:end] = self.center_volts + self.amplitude_volts
        return waveform

    def _generate_triangular_waveform(self, timing: DAQTaskTiming) -> NDArray:
        samples = timing.samples_per_cycle()
        period_start, period_end = timing.get_period_sample_range()
        # adjust the start to the beginning of the period
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

        delay_section = np.full(delay_samples, self.center_volts - self.amplitude_volts)
        rest_section = np.full(rest_samples, self.center_volts - self.amplitude_volts)
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

    def close(self):
        pass
