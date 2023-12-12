import logging
import nidaqmx
from nidaqmx.constants import FrequencyUnits as Freq
from nidaqmx.constants import Level
from nidaqmx.constants import AcquisitionType as AcqType
from nidaqmx.constants import Edge
from nidaqmx.constants import Slope
from nidaqmx.constants import TaskMode
from time import sleep

SAMPLE_MODE = {
    "finite", AcqType.FINITE
    "continuous", AcqType.CONTINUOUS
}

TRIGGER_POLARITY = {
    "rising":  Edge.RISING,
    "falling": Edge.FALLING,
}

TRIGGER_EDGE = {
    "rising":  Slope.RISING,
    "falling": Slope.FALLING,
}

RETRIGGERABLE_MODE = {
    "on": True,
    "off": False
}

TRIGGER_MODE = [
    "on",
    "off"
]

class DAQ:

    def __init__(self, dev_name: str):

        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.dev_name = dev_name
        self.dev = nidaqmx.system.device.Device(self.dev_name)
        self.ao_physical_chans = nidaqmx.system.device.ao_physical_chans
        print(self.ao_physical_chans)
        self.co_physical_chans = nidaqmx.system.device.co_physical_chans
        print(self.co_physical_chans)
        self.di_ports = nidaqmx.system.device.di_ports
        print(self.di_ports)
        self.do_ports = nidaqmx.system.device.do_ports
        print(self.do_ports)
        self.ao_max_rate = nidaqmx.system.device.ao_max_rate
        print(self.ao_max_rate)
        self.log.warning('Resetting NIDAQ')
        self.dev.reset_device()
        self.samples_per_sec = samples_per_sec
        self.tasks = list()

    def add_ao_task(self, ao_task: dict):

        self.ao_task = nidaqmx.Task(ao_task['name'])
        for channel in ao_task['channels'].items():
            channel_number = channel['number']
            if channel_number not in self.ao_physical_chans:
                raise ValueError("ao number must be one of %r." % self.ao_physical_chans)
            physical_name = f"/{self.dev_name}/{channel_number}"
            self.ao_task.ao_channels.add_ao_voltage_chan(physical_name)

        trigger_polarity = ao_task['timing']['trigger_polarity']
        valid = list(TRIGGER_POLARITY.keys())
        if trigger_polarity not in valid:
            raise ValueError("trigger polarity must be one of %r." % valid)

        trigger_mode = ao_task['timing']['trigger_mode']
        valid = TRIGGER_MODE
        if trigger_mode not in valid:
            raise ValueError("trigger mode must be one of %r." % valid)

        trigger_port = ao_task['timing']['trigger_port']
        if trigger_port not in self.di_ports:
            raise ValueError("trigger port must be one of %r." % self.di_ports)

        retriggerable = ao_task['timing']['retriggerable']
        valid = RETRIGGERABLE_MODE
        if retriggerable not in valid:
            raise ValueError("retriggerable must be one of %r." % valid)

        sample_mode = ao_task['timing']['sample_mode']
           valid = list(SAMPLE_MODE.keys())
        if sample_mode not in valid:
            raise ValueError("sample mode must be one of %r." % valid)

        period_time_ms = ao_task['timing']['period_time_ms']
        if period_time_ms < 0:
            raise ValueError("Period time must be >0 ms")

        sampling_frequency_hz = ao_tasl['timing']['sampling_frequency_hz']
        if sampling_frequency_hz < 0 or sampling_frequency_hz > self.ao_max_rate:
            raise ValueError(f"Sampling frequency must be >0 Hz and \
                             <{self.ao_max_rate} Hz!")

        daq_samples = int((period_time_ms/1000)/sampling_frequency_hz)

        if trigger_mode == "on":

            self.ao_task.timing.cfg_samp_clk_timing(
                rate = sampling_frequency,
                active_edge = TRIGGER_POLARITY[trigger_polarity],
                sample_mode = SAMPLE_MODE[sample_mode],
                samps_per_chan = self.daq_samples)

            self.ao_task.triggers.start_trigger.cfg_dig_edge_start_trig(
                trigger_source=f'/{self.dev_name}/{trigger_port}',
                trigger_edge=TRIGGER_EDGE[trigger_polarity])

            self.ao_task.triggers.start_trigger.retriggerable = retriggerable

        if trigger_mode == "off":

            self.ao_task.timing.cfg_samp_clk_timing(
                rate = sampling_frequency,
                sample_mode = SAMPLE_MODE[sample_mode],
                samps_per_chan = int((period_time_ms/1000)/sampling_frequency_hz))

        self.ao_task.out_stream.output_buf_size = self.daq_samples  # Sets buffer to length of voltages
        self.ao_task.control(TaskMode.TASK_COMMIT)

    def add_co_task(self, co_task: dict):

        self.co_task = nidaqmx.Task(co_task['name'])

        output_port = co_task['timing']['output_port']
        if output_port not in self.do_ports:
            raise ValueError("output port must be one of %r." % self.do_ports)

        period_time_ms = co_task['timing']['period_time_ms']
        if period_time_ms < 0:
            raise ValueError("Period time must be >0 ms")

        sampling_frequency_hz = co_tasl['timing']['sampling_frequency_hz']
        if sampling_frequency_hz < 0 or sampling_frequency_hz > self.ao_max_rate:
            raise ValueError(f"Sampling frequency must be >0 Hz and \
                             <{self.ao_max_rate} Hz!")

        period_frequency_hz = int(sampling_frequency_hz/(period_time_ms/1000))

        for channel in co_task['channels'].items():
            channel_number = channel['number']
            if channel_number not in self.co_physical_chans:
                raise ValueError("co number must be one of %r." % self.co_physical_chans)
            physical_name = f"/{self.dev_name}/{channel_number}"
            co_chan = self.co_task.co_channels.add_co_pulse_chan_freq(
                counter = physical_name,
                units = Freq.HZ,
                idle_state = Levl.LOW,
                initial_delay = 0.0,
                freq = period_frequency_hz,
                duty_cycle = 0.5
                )

        	co_chan.co_pulse_term = f'/{self.dev_name}/{output_port}'