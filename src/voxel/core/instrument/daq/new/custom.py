from dataclasses import dataclass

from nidaqmx.constants import ChannelType as DaqChannelType
from nidaqmx.errors import DaqError
from nidaqmx.system.device import Device as NiDevice
from nidaqmx.task import Task as NiTask
from nidaqmx.task.channels import AOChannel as NiAOChannel

from voxel.core.instrument.device.base import VoxelDeviceConnectionError


@dataclass
class DaqTiming:
    """Timing parameters for a DAQ task."""

    sample_mode: str
    sample_rate: float
    period_ms: float

    @property
    def samples_per_period(self) -> int:
        return int(self.sample_rate * self.period_ms / 1000)


class MyChannel:
    def __init__(self, name: str, task: "MyTask", inst: NiAOChannel) -> None:
        self.name = name
        self.task = task
        self.inst = inst
        self.type = DaqChannelType.ANALOG_OUTPUT


class MyTask:
    def __init__(self, name: str, daq: "MyDAQ") -> None:
        self.name = name
        self.inst = NiTask(name)
        self.daq = daq
        self.channels: dict[str, MyChannel] = {}

    def add_channel(self, channel_name: str, channel_type: DaqChannelType, port: str) -> MyChannel:
        if port not in self.daq.ports[channel_type]:
            raise ValueError(f"Port {port} is not available.")
        if channel_type == DaqChannelType.ANALOG_OUTPUT:
            self.channels[channel_name] = self._add_ao_channel(channel_name, port)
            return self.channels[channel_name]

    def _add_ao_channel(self, channel_name: str, port: str) -> MyChannel:
        inst = self.inst.ao_channels.add_ao_voltage_chan(port, channel_name)
        return MyChannel(name=channel_name, task=self, inst=inst)

    def __del__(self) -> None:
        self.inst.close()


class MyDAQ:
    def __init__(self, name: str) -> None:
        self.name = name
        self.inst = self._connect(name)

    def __repr__(self) -> str:
        return f"DAQ: {self.inst}"

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


if __name__ == "__main__":
    from pprint import pprint as print

    daq = MyDAQ("Dev1")
    # pprint(daq.ports)
    task = MyTask("TestTask", daq)
    task.add_channel("TestChannel", DaqChannelType.ANALOG_OUTPUT, "Dev1/ao0")
    print(task.channels["TestChannel"].inst)
    print(task.inst.channels)
