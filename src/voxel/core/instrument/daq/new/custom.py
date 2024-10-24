from typing import Self

import numpy as np
from nidaqmx.constants import AcquisitionType as NiAcquisitionType
from nidaqmx.constants import ChannelType as DaqChannelType
from nidaqmx.errors import DaqError, DaqResourceWarning
from nidaqmx.system import System
from nidaqmx.system.device import Device as NiDevice
from nidaqmx.task import Task as NiTask
from nidaqmx.task.channels import AOChannel as NiAOChannel

from voxel.core.instrument.daq.new.waveform import DaqTiming, Waveform
from voxel.core.instrument.device.base import VoxelDeviceConnectionError
from voxel.core.utils.logging import get_component_logger


class Daq:
    def __init__(self, name: str) -> None:
        self.name = name
        self.system = System.local()
        self.inst = self._connect(name)
        self.used_ports = set()

    def __repr__(self) -> str:
        return f"DAQ: {self.inst} \n" f"Ports: {self.ports} \n" f"Used Ports: {self.used_ports}"

    def _connect(self, name: str) -> NiDevice:
        try:
            nidaq = NiDevice(name)
            nidaq.reset_device()
            return nidaq
        except DaqError as e:
            raise VoxelDeviceConnectionError(f"Unable to connect to DAQ device: {e}")

    @property
    def ports(self) -> dict[DaqChannelType, list[str]]:
        return {
            DaqChannelType.ANALOG_INPUT: self.inst.ai_physical_chans.channel_names,
            DaqChannelType.ANALOG_OUTPUT: self.inst.ao_physical_chans.channel_names,
            DaqChannelType.COUNTER_INPUT: self.inst.ci_physical_chans.channel_names,
            DaqChannelType.COUNTER_OUTPUT: self.inst.co_physical_chans.channel_names,
            DaqChannelType.DIGITAL_OUTPUT: self.inst.do_ports.channel_names,
            DaqChannelType.DIGITAL_INPUT: self.inst.di_ports.channel_names,
        }

    def clean_up(self) -> None:
        """Close all tasks and release ports."""
        for task in list(self.system.tasks):
            print(f"Cleaning up task: {task.name}")
            task.close()
        self.used_ports.clear()


class DaqAOChannel:
    def __init__(self, name: str, task: "DaqAOTask", inst: NiAOChannel, apply_filter: bool) -> None:
        self.name = name
        self.task = task
        self.inst = inst
        self.wave = Waveform(name=f"{self.name}_waveform", timing=self.task.timing, apply_filter=apply_filter)


class DaqAOTask:
    """A wrapper class for a nidaqmx DAQ Task. The nidaqmx Task API can still be accessed via the inst attribute."""

    def __init__(self, name: str, daq: "Daq", sampling_rate_hz: int, period_ms: float) -> None:
        self.name = name
        self.inst = NiTask(name)
        self.daq = daq
        self.log = get_component_logger(self)

        self.channels: dict[str, DaqAOChannel] = {}
        self.waveforms: np.ndarray = np.array([])

        self._period_ms = period_ms
        self._sampling_rate = sampling_rate_hz

        self.sampling_rate = sampling_rate_hz
        self.period_ms = period_ms

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}[{self.name}] \n"
            f"  timing={self.timing} \n"
            f"  channels={list(self.channels.keys())}"
        )

    @property
    def period_ms(self) -> float:
        return self._period_ms

    @period_ms.setter
    def period_ms(self, period: float) -> None:
        self._period_ms = period
        if self.channels:
            self._cfg_timing()
            self.regenerate_waveforms()

    @property
    def sampling_rate(self) -> float:
        return self.inst.timing.samp_clk_rate

    @sampling_rate.setter
    def sampling_rate(self, sample_rate: float) -> None:
        self._sampling_rate = sample_rate
        if self.channels:
            self._cfg_timing()
            self.regenerate_waveforms()

    @property
    def timing(self) -> DaqTiming:
        return DaqTiming(sampling_rate=self.sampling_rate, period_ms=self.period_ms)

    def add_channel(self, name: str, port: str, apply_filter: bool = False) -> DaqAOChannel:
        port = f"{self.daq.name}/{port}"
        available_ports = [
            port for port in self.daq.ports[DaqChannelType.ANALOG_OUTPUT] if port not in self.daq.used_ports
        ]
        if port not in available_ports:
            raise ValueError(
                f"Port {port} is not available for analog output.\n" f"  Available ports: {available_ports}"
            )
        channel_inst = self.inst.ao_channels.add_ao_voltage_chan(port, name)
        channel = DaqAOChannel(name=name, task=self, inst=channel_inst, apply_filter=apply_filter)
        self.channels[name] = channel
        self.daq.used_ports.add(port)
        self._cfg_timing()
        return self.channels[name]

    def regenerate_waveforms(self) -> None:
        for channel in self.channels.values():
            channel.wave.regenerate()

    def write(self) -> np.ndarray:
        inst_names = self.inst.channels.channel_names
        expected_samples = len(inst_names) * self.timing.samples_per_period
        self.regenerate_waveforms()
        data = np.concatenate([self.channels[name].wave.data for name in inst_names])
        if data.size != expected_samples:
            self.log.warning(f"Only wrote {data.size} samples out of {expected_samples} requested.")
        written_samples = self.inst.write(data)
        if written_samples != expected_samples:
            self.log.warning(f"Only wrote {written_samples} samples out of {expected_samples} requested.")
        return data

    def release_ports(self) -> None:
        for channel in self.channels.values():
            port = channel.inst.physical_channel
            self.daq.used_ports.remove(port)

    def close(self, release_ports: bool = False) -> None:
        try:
            self.inst.close()
        except DaqError as e:
            self.log.error(f"Error closing task: {e}")
        if release_ports:
            self.release_ports()

    def _cfg_timing(self) -> None:
        self.inst.timing.cfg_samp_clk_timing(
            rate=self.sampling_rate,
            sample_mode=NiAcquisitionType.CONTINUOUS,
            samps_per_chan=self.timing.samples_per_period,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def __del__(self) -> None:
        """Ensure resources are released when the object is deleted."""
        try:
            self.release_ports()
            self.inst.close()
        except (DaqResourceWarning, DaqError):
            pass


if __name__ == "__main__":
    from pprint import pprint as print

    daq = Daq("Dev1")
    task = DaqAOTask(name="TestTask1", daq=daq, sampling_rate_hz=1e6, period_ms=100)
    test_channel = task.add_channel(name="TestChannel", port="ao0", apply_filter=True)
    test_channel.wave.apply_filter = True
    print(daq)
    print(task)
    with task:
        for _, channel in task.channels.items():
            print(channel.wave)
            channel.wave.plot()

    daq.clean_up()
