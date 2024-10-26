from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, Self

import numpy as np
from nidaqmx.constants import AcquisitionType as NiAcquisitionType

# from nidaqmx.constants import ChannelType as DaqChannelType
from nidaqmx.errors import DaqError, DaqResourceWarning
from nidaqmx.system import System
from nidaqmx.system.device import Device as NiDevice
from nidaqmx.task import Task as NiTask
from nidaqmx.task.channels import AOChannel as NiAOChannel
from nidaqmx.task.channels import DOChannel as NiDOChannel

from voxel.core.instrument.daq.new.waveform import DaqTiming, Waveform
from voxel.core.instrument.device.base import VoxelDeviceConnectionError
from voxel.core.utils.logging import get_component_logger


class NiDaqModel(StrEnum):
    """Enumeration of supported NI DAQ models."""

    NI6738 = "6738"
    NI6739 = "6739"
    OTHER = "other"


DEVICE_CONFIGS = {
    NiDaqModel.NI6738: {
        "ao_split": 16,  # AO channels 0-15 on connector 0, 16-31 on connector 1
        "dio_lines": 2,  # 2 DIO lines total
        "pfi_lines": 8,  # 8 PFI lines total
    },
    NiDaqModel.NI6739: {
        "ao_split": 32,  # AO channels 0-31 on connector 0, 32-63 on connector 1
        "dio_lines": 4,  # 4 DIO lines total
        "pfi_lines": 16,  # 16 PFI lines total
    },
}


@dataclass
class PinInfo:
    connection: str
    pfi: str | None
    counter: str | None
    assigned: bool = False


PORT_MAP = {
    NiDaqModel.NI6738: {
        "P0.0": PinInfo(connection="port0/line0", pfi=None, counter=None),
        "P0.1": PinInfo(connection="port0/line1", pfi=None, counter=None),
        "P1.0": PinInfo(connection="port1/line0", pfi="pfi0", counter="ctr1/src"),
        "P1.1": PinInfo(connection="port1/line1", pfi="pfi1", counter="ctr1/gate"),
        "P1.2": PinInfo(connection="port1/line2", pfi="pfi2", counter="ctr1/out"),
        "P1.3": PinInfo(connection="port1/line3", pfi="pfi3", counter="ctr1/aux"),
        "P1.4": PinInfo(connection="port1/line4", pfi="pfi4", counter="ctr0/aux"),
        "P1.5": PinInfo(connection="port1/line5", pfi="pfi5", counter="ctr0/src"),
        "P1.6": PinInfo(connection="port1/line6", pfi="pfi6", counter="ctr0/gate"),
        "P1.7": PinInfo(connection="port1/line7", pfi="pfi7", counter="ctr0/out"),
    },
    NiDaqModel.NI6739: {
        "P0.0": PinInfo(connection="port0/line0", pfi=None, counter=None),
        "P0.1": PinInfo(connection="port0/line1", pfi=None, counter=None),
        "P0.2": PinInfo(connection="port0/line2", pfi=None, counter=None),
        "P0.3": PinInfo(connection="port0/line3", pfi=None, counter=None),
        "P1.0": PinInfo(connection="port1/line0", pfi="pfi0", counter="ctr1/src"),
        "P1.1": PinInfo(connection="port1/line1", pfi="pfi1", counter="ctr1/gate"),
        "P1.2": PinInfo(connection="port1/line2", pfi="pfi2", counter="ctr1/out"),
        "P1.3": PinInfo(connection="port1/line3", pfi="pfi3", counter="ctr1/aux"),
        "P1.4": PinInfo(connection="port1/line4", pfi="pfi4", counter="ctr0/aux"),
        "P1.5": PinInfo(connection="port1/line5", pfi="pfi5", counter="ctr0/src"),
        "P1.6": PinInfo(connection="port1/line6", pfi="pfi6", counter="ctr0/gate"),
        "P1.7": PinInfo(connection="port1/line7", pfi="pfi7", counter="ctr0/out"),
        "P2.0": PinInfo(connection="port2/line0", pfi="pfi8", counter="ctr3/src"),
        "P2.1": PinInfo(connection="port2/line1", pfi="pfi9", counter="ctr3/gate"),
        "P2.2": PinInfo(connection="port2/line2", pfi="pfi10", counter="ctr3/out"),
        "P2.3": PinInfo(connection="port2/line3", pfi="pfi11", counter="ctr3/aux"),
        "P2.4": PinInfo(connection="port2/line4", pfi="pfi12", counter="ctr2/aux"),
        "P2.5": PinInfo(connection="port2/line5", pfi="pfi13", counter="ctr2/src"),
        "P2.6": PinInfo(connection="port2/line6", pfi="pfi14", counter="ctr2/gate"),
        "P2.7": PinInfo(connection="port2/line7", pfi="pfi15", counter="ctr2/out"),
    },
}


class Daq:
    def __init__(self, name: str) -> None:
        self.name = name
        self.log = get_component_logger(self)
        self.system = System.local()
        self.inst = self._connect(name)
        self.model = self._assign_model()
        self.config = DEVICE_CONFIGS[self.model]
        self.ao_pins = self._get_analog_pins()
        self.dio_pins = self._get_digital_pins()

    def __repr__(self) -> str:
        return f"DAQ Device: {self.name} ({self.model})\n" f"Pins: {list(self.pins.items())}"

    def _connect(self, name: str) -> NiDevice:
        """Connect to DAQ device."""
        try:
            nidaq = NiDevice(name)
            nidaq.reset_device()
            return nidaq
        except DaqError as e:
            raise VoxelDeviceConnectionError(f"Unable to connect to DAQ device: {e}")

    def _assign_model(self) -> NiDaqModel:
        """Determine DAQ model from device info."""
        if "6738" in self.inst.product_type:
            return NiDaqModel.NI6738
        elif "6739" in self.inst.product_type:
            return NiDaqModel.NI6739
        else:
            self.log.warning(f"DAQ model {self.inst.product_type} may not be fully supported.")
            return NiDaqModel.OTHER

    def _get_analog_pins(self) -> dict[str, PinInfo]:
        """Get analog output pins."""
        pins = {}
        for ao_channel_name in self.inst.ao_physical_chans.channel_names:
            name = ao_channel_name.split("/")[-1].upper()
            pins[name] = PinInfo(connection=ao_channel_name, pfi=None, counter=None)
        return pins

    def _get_digital_pins(self) -> dict[str, PinInfo]:
        """Get digital I/O pins including PFI and counter mappings."""
        pins = {}
        for dio_channel in self.inst.do_lines.channel_names:
            parts = dio_channel.upper().split("/")
            port_num = int(parts[-2].replace("PORT", ""))
            line_num = int(parts[-1].replace("LINE", ""))
            pin_key = f"P{port_num}.{line_num}"
            if pin_key in PORT_MAP[self.model]:
                pins[pin_key] = PORT_MAP[self.model][pin_key]
        return pins

    @property
    def pins(self) -> dict[str, PinInfo]:
        """Get all pins (analog and digital)."""
        return {**self.ao_pins, **self.dio_pins}

    @property
    def pfi_ports(self) -> dict[str, PinInfo]:
        """Get PFI ports."""
        return {key: value for key, value in self.dio_pins.items() if value.pfi is not None}

    def is_pin_available(self, pin: str) -> bool:
        """Check if a pin is available for assignment."""
        return pin in self.pins and not self.pins[pin].assigned

    def assign_ao_pin(self, pin: str) -> PinInfo:
        """Assign an analog output pin."""
        if pin not in self.ao_pins:
            raise ValueError(f"Pin {pin} is not an analog output pin.")
        pin = self.ao_pins[pin]
        if pin.assigned:
            raise ValueError(f"Pin {pin} is already assigned.")
        pin.assigned = True
        return pin

    def assign_dio_pin(self, pin: str) -> PinInfo:
        """Assign a digital I/O pin."""
        if pin.startswith("PFI"):
            pin = self._get_pin_from_pfi(pin)
        if pin not in self.dio_pins:
            raise ValueError(f"Pin {pin} is not a digital I/O pin.")
        pin = self.dio_pins[pin]
        if pin.assigned:
            raise ValueError(f"Pin {pin} is already assigned.")
        pin.assigned = True
        return pin

    def release_pin(self, connection: str) -> bool:
        """Release a previously assigned port.
        Returns True if successful, False if the port was not assigned.
        """
        for pin in self.pins.values():
            if pin.connection == connection:
                if pin.assigned:
                    pin.assigned = False
                    return True
                return False
        return False

    def clean_up(self) -> None:
        """Close all tasks and release ports."""
        for task in list(self.system.tasks):
            print(f"Cleaning up task: {task.name}")
            task.close()

    def _get_pin_from_pfi(self, pfi: str) -> str | None:
        """Get the corresponding pin for a given PFI."""
        for pin, info in self.dio_pins.items():
            if info.pfi == pfi:
                return pin
        return None


class TriggerSourceTask:
    """A wrapper class for a nidaqmx DAQ Task managing counter channels used for triggering events.
    :param name: The name of the task. Also used as the task identifier in nidaqmx.
    :param daq: A reference to the Daq object.
    :param pin: The pin to use for triggering. Notation is either "P1.X" or "PFI.X".
    :param freq_hz: The frequency of the trigger signal in Hz.
    :param duty_cycle: The duty cycle of the trigger signal as a fraction (0.0 to 1.0), default is 0.5.
    :param initial_delay_ms: The initial delay before the trigger signal starts, in milliseconds, default is 0.
    :param idle_state: The idle state of the trigger signal ("HIGH" or "LOW"), default is "LOW"
    :type freq_hz: float
    :type duty_cycle: float
    :type initial_delay_ms: float
    :type idle_state: Literal["HIGH", "LOW"]
    """

    def __init__(
        self,
        name: str,
        daq: Daq,
        pin: str,
        freq_hz: float,
        duty_cycle: float = 0.5,
        initial_delay_ms: float = 0.0,
        idle_state: Literal["HIGH", "LOW"] = "LOW",
    ) -> None:
        self.name = name
        self.daq = daq
        self.inst = NiTask(name)

        self.freq_hz = freq_hz
        self.duty_cycle = duty_cycle
        self.initial_delay_ms = initial_delay_ms
        self.idle_state = idle_state

        self.pin = self.daq.assign_dio_pin(pin)

        self.channel = self._create_co_channel()
        self.inst.timing.cfg_implicit_timing(sample_mode=NiAcquisitionType.CONTINUOUS)

    def __setattr__(self, name, value) -> None:
        super().__setattr__(name, value)
        if name in ("freq_hz", "duty_cycle", "initial_delay_ms", "idle_state"):
            self._reconfigure_task()

    def _reconfigure_task(self) -> None:
        self.channel = self._create_co_channel()

    def _create_co_channel(self) -> None:
        """Create a counter output channel for triggering."""
        return self.inst.co_channels.add_co_pulse_chan_freq(
            self.pin.connection,
            name_to_assign_to_channel=self.name,
            freq=self.freq_hz,
            duty_cycle=self.duty_cycle,
            initial_delay=self.initial_delay_ms,
            idle_state=self.idle_state,
        )

    def start(self) -> None:
        """Start generating trigger pulses."""
        self.task.start()

    def stop(self) -> None:
        """Stop generating trigger pulses."""
        self.task.stop()

    def close(self) -> None:
        """Clean up resources."""
        try:
            self.stop()
            self.task.close()
            self.daq.release_pin(self.daq.dio_pins[self.pin].connection)
        except Exception as e:
            self.daq.log.error(f"Error closing trigger task: {e}")

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


class WaveGenChannel:
    def __init__(
        self, name: str, task: "WaveGenTask", inst: NiAOChannel | NiDOChannel, apply_filter: bool, is_digital: bool
    ) -> None:
        self.name = name
        self.task = task
        self.inst = inst
        self.wave = Waveform(
            name=f"{self.name}_waveform", timing=self.task.timing, apply_filter=apply_filter, is_digital=is_digital
        )


class WaveGenTask:
    """A wrapper class for a nidaqmx DAQ Task managing analog and digital output channels.
    :param name: The name of the task. Also used as the task identifier in nidaqmx.
    :param daq: A reference to the Daq object.
    :param sampling_rate_hz: The sampling rate in Hz.
    :param period_ms: The period of the waveform in milliseconds.
    :param trigger_source: Optional trigger source for the task.
    :type name: str
    :type daq: Daq
    :type sampling_rate_hz: float
    :type period_ms: float
    :type trigger: TriggerSource | None
    Note:
        - This task is designed for generating waveforms on AO and DO channels.
        - The nidaqmx Task API can still be accessed via the inst attribute.
    """

    def __init__(
        self,
        name: str,
        daq: "Daq",
        sampling_rate_hz: int,
        period_ms: float,
        trigger: TriggerSourceTask | None = None,
    ) -> None:
        self.name = name
        self.inst = NiTask(name)
        self.daq = daq
        self.log = get_component_logger(self)

        self.channels: dict[str, WaveGenChannel] = {}
        self.waveforms: np.ndarray = np.array([])

        self._period_ms = period_ms
        self._sampling_rate = sampling_rate_hz

        self.sampling_rate = sampling_rate_hz
        self.period_ms = period_ms

        self._sample_mode = NiAcquisitionType.FINITE
        self._trigger = trigger
        if self._trigger:
            self._cfg_start_trigger()
            self._sample_mode = NiAcquisitionType.CONTINUOUS

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

    def add_ao_channel(self, name: str, pin: str, apply_filter: bool = True) -> WaveGenChannel:
        """Add an analog output channel to the task."""
        pin = pin.upper()
        if not self.daq.is_pin_available(pin):
            raise ValueError(f"AO pin {pin} is not available. Available pins: {self.daq.ao_pins.items()}")
        physical_channel = self.daq.pins[pin].connection
        channel_inst = self.inst.ao_channels.add_ao_voltage_chan(physical_channel, name)
        channel = WaveGenChannel(name=name, task=self, inst=channel_inst, apply_filter=apply_filter, is_digital=False)
        self.channels[name] = channel
        self.daq.assign_ao_pin(pin)
        self._cfg_timing()
        return self.channels[name]

    def add_do_channel(self, name: str, pin: str, apply_filter: bool = False) -> WaveGenChannel:
        """Add an analog output channel to the task."""
        pin = pin.upper()
        if not self.daq.is_pin_available(pin):
            raise ValueError(f"AO pin {pin} is not available. Available pins: {self.daq.ao_pins.items()}")
        physical_channel = self.daq.pins[pin].connection
        channel_inst = self.inst.ao_channels.add_ao_voltage_chan(physical_channel, name)
        channel = WaveGenChannel(name=name, task=self, inst=channel_inst, apply_filter=apply_filter, is_digital=True)
        self.channels[name] = channel
        self.daq.assign_ao_pin(pin)
        self._cfg_timing()
        return self.channels[name]

    def regenerate_waveforms(self) -> None:
        for channel in self.channels.values():
            channel.wave.regenerate()

    def write(self) -> np.ndarray:
        inst_names = self.inst.channels.channel_names
        self.regenerate_waveforms()
        # data needs to be a 2D array with shape (channels, samples)
        data = np.array([self.channels[name].wave.data for name in inst_names])
        self.log.info(f"writing {data.shape} data to {self.inst.name}")
        written_samples = self.inst.write(data)
        if written_samples != self.timing.samples_per_period:
            self.log.warning(f"Only wrote {written_samples} samples out of {self.timing.samples_per_period} requested.")
        return data

    def start(self) -> None:
        self.inst.start()

    def stop(self) -> None:
        self.inst.stop()

    def release_pins(self) -> None:
        for channel in self.channels.values():
            self.daq.release_pin(channel.inst.physical_channel)

    def close(self) -> None:
        try:
            self.release_pins()
            self.inst.close()
        except DaqError as e:
            self.log.error(f"Error closing task: {e}")

    def _cfg_timing(self) -> None:
        self.inst.timing.cfg_samp_clk_timing(
            rate=self.sampling_rate,
            sample_mode=self._sample_mode,
            samps_per_chan=self.timing.samples_per_period,
        )

    def _cfg_start_trigger(self) -> None:
        pass

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def __del__(self) -> None:
        """Ensure resources are released when the object is deleted."""
        try:
            self.release_pins()
            self.inst.close()
        except (DaqResourceWarning, DaqError):
            pass


def plot_waveforms(task: WaveGenTask):
    from matplotlib import pyplot as plt

    _, ax = plt.subplots()
    for _, channel in task.channels.items():
        channel.wave.plot(ax=ax)

    plt.ion()
    plt.show()
    plt.pause(0.1)


def run_task(task: WaveGenTask, duration: int = 30) -> None:
    with task:
        task.write()
        task.start()

        import time

        time.sleep(duration)

        task.stop()


if __name__ == "__main__":
    from pprint import pprint as print

    # channels
    # test1 -> ao20 (oscilloscope 1)
    # galvo -> ao0 (oscilloscope 2)
    # test2 -> ao4 (ad2 1)
    # clk   -> pf10 (ad2 2)

    daq = Daq("Dev1")

    task = WaveGenTask(name="TestTask", daq=daq, sampling_rate_hz=1e6, period_ms=100, trigger=TriggerSourceTask())
    test1 = task.add_ao_channel(name="test1-ao20-ch1", pin="ao20")
    galvo = task.add_ao_channel(name="galvo-ch2", pin="ao0")
    test2 = task.add_do_channel(name="test2-ad2-1", pin="ao4")

    # task.inst.triggers.start_trigger.dig_edge_src = daq.pfi_ports["P1.0"].pfi
    # print(task.inst.triggers.start_trigger.dig_edge_src)

    run_task(task, duration=10)

    daq.clean_up()
