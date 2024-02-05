import logging
import nidaqmx
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
from scipy import signal
from nidaqmx.constants import FrequencyUnits as Freq
from nidaqmx.constants import Level
from nidaqmx.constants import AcquisitionType as AcqType
from nidaqmx.constants import Edge
from nidaqmx.constants import Slope
from nidaqmx.constants import TaskMode

DO_WAVEFORMS = [
    'square wave'
]

AO_WAVEFORMS = [
    'square wave',
    'sawtooth',
    'triangle wave'
]

TRIGGER_MODE = [
    "on",
    "off"
]

SAMPLE_MODE = {
    "finite": AcqType.FINITE,
    "continuous": AcqType.CONTINUOUS
}

TRIGGER_POLARITY = {
    "rising":  Edge.RISING,
    "falling": Edge.FALLING
}

TRIGGER_EDGE = {
    "rising":  Slope.RISING,
    "falling": Slope.FALLING,
}

RETRIGGERABLE_MODE = {
    "on": True,
    "off": False
}

class DAQ:

    def __init__(self, dev: str):

        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.devs = list()
        for device in nidaqmx.system.System.local().devices:
            self.devs.append(device.name)
        print(dev, self.devs)
        if dev not in self.devs:
            raise ValueError("dev name must be one of %r." % self.devs)        
        self.id = dev
        self.dev = nidaqmx.system.device.Device(self.id)
        self.ao_physical_chans = self.dev.ao_physical_chans.channel_names
        self.ao_physical_chans = [channel.replace(f'{self.id}/', "") for channel in self.ao_physical_chans]
        self.co_physical_chans = self.dev.co_physical_chans.channel_names
        self.co_physical_chans = [channel.replace(f'{self.id}/', "") for channel in self.co_physical_chans]
        self.dio_ports = self.dev.do_ports.channel_names
        self.dio_ports = [channel.replace(f'{self.id}/', "") for channel in self.dio_ports]
        self.dio_ports = [channel.replace(f'port', "PFI") for channel in self.dio_ports]
        self.dio_lines = self.dev.do_lines.channel_names
        self.max_ao_rate = self.dev.ao_max_rate
        self.min_ao_rate = self.dev.ao_min_rate
        self.max_do_rate = self.dev.do_max_rate
        self.max_ao_volts = self.dev.ao_voltage_rngs[1]
        self.min_ao_volts = self.dev.ao_voltage_rngs[0]
        self.log.info('resetting nidaq')
        self.dev.reset_device()
        self.tasks = list()
        self.ao_waveforms = dict()
        self.do_waveforms = dict()

    def add_ao_task(self, ao_task: dict):

        self.ao_task = nidaqmx.Task(ao_task['name'])

        trigger_polarity = ao_task['timing']['trigger_polarity']
        valid = list(TRIGGER_POLARITY.keys())
        if trigger_polarity not in valid:
            raise ValueError("trigger polarity must be one of %r." % valid)

        trigger_mode = ao_task['timing']['trigger_mode']
        valid = TRIGGER_MODE
        if trigger_mode not in valid:
            raise ValueError("trigger mode must be one of %r." % valid)

        trigger_port = ao_task['timing']['trigger_port']
        if trigger_port not in self.dio_ports:
            raise ValueError("trigger port must be one of %r." % self.dio_ports)

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

        rest_time_ms = ao_task['timing']['rest_time_ms']
        if rest_time_ms < 0:
            raise ValueError("Period time must be >0 ms")

        sampling_frequency_hz = ao_task['timing']['sampling_frequency_hz']
        if sampling_frequency_hz < self.min_ao_rate or sampling_frequency_hz > self.max_ao_rate:
            raise ValueError(f"Sampling frequency must be >{self.min_ao_rate} Hz and \
                             <{self.max_ao_rate} Hz!")

        for channel in ao_task['ports']:
            # add channel to task
            channel_port = channel['port']
            if channel_port not in self.ao_physical_chans:
                raise ValueError("ao number must be one of %r." % self.ao_physical_chans)
            physical_name = f"/{self.id}/{channel_port}"
            self.ao_task.ao_channels.add_ao_voltage_chan(physical_name)

        total_time_ms = period_time_ms + rest_time_ms
        daq_samples = int(((total_time_ms)/1000)*sampling_frequency_hz)

        if trigger_mode == "on":

            self.ao_task.timing.cfg_samp_clk_timing(
                rate = sampling_frequency_hz,
                active_edge = TRIGGER_POLARITY[trigger_polarity],
                sample_mode = SAMPLE_MODE[sample_mode],
                samps_per_chan = daq_samples)

            self.ao_task.triggers.start_trigger.cfg_dig_edge_start_trig(
                trigger_source=f'/{self.id}/{trigger_port}',
                trigger_edge=TRIGGER_EDGE[trigger_polarity])

            self.ao_task.triggers.start_trigger.retriggerable = RETRIGGERABLE_MODE[retriggerable]

        if trigger_mode == "off":

            self.ao_task.timing.cfg_samp_clk_timing(
                rate = sampling_frequency,
                sample_mode = SAMPLE_MODE[sample_mode],
                samps_per_chan = int((period_time_ms/1000)/sampling_frequency_hz))

        self.ao_task.out_stream.output_buf_size = daq_samples  # Sets buffer to length of voltages
        self.ao_task.control(TaskMode.TASK_COMMIT)
        self.ao_task.ao_line_states_done_state = Level.LOW
        self.ao_task.ao_line_states_paused_state = Level.LOW

        self.tasks.append(self.ao_task)

    def generate_ao_waveforms(self, ao_task: dict, wavelength: str):

        period_time_ms = ao_task['timing']['period_time_ms']
        if period_time_ms < 0:
            raise ValueError("Period time must be >0 ms")

        rest_time_ms = ao_task['timing']['rest_time_ms']
        if rest_time_ms < 0:
            raise ValueError("Period time must be >0 ms")

        sampling_frequency_hz = ao_task['timing']['sampling_frequency_hz']
        if sampling_frequency_hz < 0 or sampling_frequency_hz > self.max_ao_rate:
            raise ValueError(f"Sampling frequency must be >0 Hz and \
                             <{self.max_ao_rate} Hz!")

        # store these values as properties for plotting purposes
        self.ao_sampling_frequency_hz = sampling_frequency_hz
        self.ao_total_time_ms = period_time_ms + rest_time_ms

        for channel in ao_task['ports']:
            # load waveform and variables
            port = channel['port']
            name = channel['name']
            device_min_volts = channel['device_min_volts']
            device_max_volts = channel['device_max_volts']
            waveform = channel['waveform']
            valid = AO_WAVEFORMS
            if waveform not in AO_WAVEFORMS:
                raise ValueError("waveform must be one of %r." % valid)
            if waveform == 'square wave':
                try:
                    start_time_ms = channel['parameters']['start_time_ms']['channels'][wavelength]
                    if start_time_ms > period_time_ms:
                        raise ValueError("start time must be < period time")
                    end_time_ms = channel['parameters']['end_time_ms']['channels'][wavelength]
                    if end_time_ms > period_time_ms or end_time_ms < start_time_ms:
                        raise ValueError("end time must be < period time and > start time")
                    max_volts = channel['parameters']['max_volts']['channels'][wavelength]
                    if max_volts > self.max_ao_volts:
                        raise ValueError(f"max volts must be < {self.max_ao_volts} volts")
                    min_volts = channel['parameters']['min_volts']['channels'][wavelength]
                    if min_volts < self.min_ao_volts:
                        raise ValueError(f"min volts must be > {self.min_ao_volts} volts")
                except:
                    raise ValueError("missing input parameter for square wave")
                voltages = self.square_wave(sampling_frequency_hz,
                                             period_time_ms,
                                             start_time_ms,
                                             end_time_ms,
                                             rest_time_ms,
                                             max_volts,
                                             min_volts
                                             )

            if waveform == 'sawtooth':
                try:
                    start_time_ms = channel['parameters']['start_time_ms']['channels'][wavelength]
                    if start_time_ms > period_time_ms:
                        raise ValueError("start time must be < period time")
                    end_time_ms = channel['parameters']['end_time_ms']['channels'][wavelength]
                    if end_time_ms > period_time_ms or end_time_ms < start_time_ms:
                        raise ValueError("end time must be < period time and > start time")
                    amplitude_volts = channel['parameters']['amplitude_volts']['channels'][wavelength]
                    offset_volts = channel['parameters']['offset_volts']['channels'][wavelength]
                    if offset_volts < self.min_ao_volts or offset_volts > self.max_ao_volts:
                        raise ValueError(f"min volts must be > {self.min_ao_volts} volts and < {self.max_ao_volts} volts")
                    cutoff_frequency_hz = channel['parameters']['cutoff_frequency_hz']['channels'][wavelength]
                    if cutoff_frequency_hz < 0:
                        raise ValueError(f"cutoff frequnecy must be > 0 Hz")
                except:
                    raise ValueError("missing input parameter for sawtooth")
                voltages = self.sawtooth(sampling_frequency_hz,
                                         period_time_ms,
                                         start_time_ms,
                                         end_time_ms,
                                         rest_time_ms,
                                         amplitude_volts,
                                         offset_volts,
                                         cutoff_frequency_hz
                                        )
            if waveform == 'triangle wave':
                try:
                    start_time_ms = channel['parameters']['start_time_ms']['channels'][wavelength]
                    if start_time_ms > period_time_ms:
                        raise ValueError("start time must be < period time")
                    end_time_ms = channel['parameters']['end_time_ms']['channels'][wavelength]
                    if end_time_ms > period_time_ms or end_time_ms < start_time_ms:
                        raise ValueError("end time must be < period time and > start time")
                    amplitude_volts = channel['parameters']['amplitude_volts']['channels'][wavelength]
                    offset_volts = channel['parameters']['offset_volts']['channels'][wavelength]
                    if offset_volts < self.min_ao_volts or offset_volts > self.max_ao_volts:
                        raise ValueError(f"min volts must be > {self.min_ao_volts} volts and < {self.max_ao_volts} volts")
                    cutoff_frequency_hz = channel['parameters']['cutoff_frequency_hz']['channels'][wavelength]
                    if cutoff_frequency_hz < 0:
                        raise ValueError(f"cutoff frequnecy must be > 0 Hz")
                except:
                    raise ValueError("missing input parameter for triangle wave")
                voltages = self.triangle_wave(sampling_frequency_hz,
                                             period_time_ms,
                                             start_time_ms,
                                             end_time_ms,
                                             rest_time_ms,
                                             amplitude_volts,
                                             offset_volts,
                                             cutoff_frequency_hz
                                            )

            # sanity check voltages for ni card range
            if numpy.max(voltages[:]) > self.max_ao_volts or numpy.min(voltages[:]) < self.min_ao_volts:
                raise ValueError(f"voltages are out of ni card range [{self.min_ao_volts}, {self.max_ao_volts}] volts")

            # sanity check voltages for device range
            if numpy.max(voltages[:]) > device_max_volts or numpy.min(voltages[:]) < device_min_volts:
                raise ValueError(f"voltages are out of device range [{device_min_volts}, {device_max_volts}] volts")

            # store 1d voltage array into 2d waveform array
            self.ao_waveforms[f"{port}: {name}"] = voltages

    def write_ao_waveforms(self):

        ao_voltages = list()
        for waveform in self.ao_waveforms:
            ao_voltages.append(self.ao_waveforms[waveform])
        ao_voltages = numpy.array(ao_voltages)

        # unreserve buffer
        self.ao_task.control(TaskMode.TASK_UNRESERVE)
        # sets buffer to length of voltages
        self.ao_task.out_stream.output_buf_size = len(ao_voltages[0])
        self.ao_task.control(TaskMode.TASK_COMMIT)

        self.ao_task.write(numpy.array(ao_voltages))

    def add_co_task(self, co_task: dict, pulse_count: int = None):

        self.co_task = nidaqmx.Task(co_task['name'])

        output_port = co_task['timing']['output_port']
        if output_port not in self.dio_ports:
            raise ValueError("output port must be one of %r." % self.do_ports)

        frequency_hz = co_task['timing']['frequency_hz']
        if frequency_hz < 0:
            raise ValueError(f"frequency must be >0 Hz")

        for channel in co_task['counters']:
            channel_number = channel['counter']
            if channel_number not in self.co_physical_chans:
                raise ValueError("co number must be one of %r." % self.co_physical_chans)
            physical_name = f"/{self.id}/{channel_number}"
            co_chan = self.co_task.co_channels.add_co_pulse_chan_freq(
                counter = physical_name,
                units = Freq.HZ,
                freq = frequency_hz,
                duty_cycle = 0.5
                )

            co_chan.co_pulse_term = f'/{self.id}/{output_port}'

            optional_kwds = {}
            # don't specify samps_per_chan to use default value if it was specified
            # as 0 or None.
            if pulse_count:
                optional_kwds['samps_per_chan'] = pulse_count
            self.co_task.timing.cfg_implicit_timing(
                sample_mode=AcqType.FINITE if pulse_count else AcqType.CONTINUOUS,
                **optional_kwds)

        self.tasks.append(self.co_task)

    def add_do_task(self, do_task: dict):

        self.do_task = nidaqmx.Task(do_task['name'])

        for channel in do_task['ports']:
            channel_number = channel['port']
            if channel_number not in self.dio_ports:
                raise ValueError("do port must be one of %r." % self.dio_ports)
            physical_name = f"/{self.id}/{channel_number}"
            self.do_task.do_channels.add_do_chan(physical_name)

        trigger_polarity = do_task['timing']['trigger_polarity']
        valid = list(TRIGGER_POLARITY.keys())
        if trigger_polarity not in valid:
            raise ValueError("trigger polarity must be one of %r." % valid)

        trigger_mode = do_task['timing']['trigger_mode']
        valid = TRIGGER_MODE
        if trigger_mode not in valid:
            raise ValueError("trigger mode must be one of %r." % valid)

        trigger_port = do_task['timing']['trigger_port']
        if trigger_port not in self.dio_ports:
            raise ValueError("trigger port must be one of %r." % self.dio_ports)

        retriggerable = do_task['timing']['retriggerable']
        valid = RETRIGGERABLE_MODE
        if retriggerable not in valid:
            raise ValueError("retriggerable must be one of %r." % valid)

        sample_mode = do_task['timing']['sample_mode']
        valid = list(SAMPLE_MODE.keys())
        if sample_mode not in valid:
            raise ValueError("sample mode must be one of %r." % valid)

        period_time_ms = do_task['timing']['period_time_ms']
        if period_time_ms < 0:
            raise ValueError("Period time must be >0 ms")

        sampling_frequency_hz = do_task['timing']['sampling_frequency_hz']
        if sampling_frequency_hz < 0 or sampling_frequency_hz > self.max_ao_rate:
            raise ValueError(f"Sampling frequency must be >0 Hz and \
                             <{self.max_ao_rate} Hz!")

        daq_samples = int((period_time_ms/1000)*sampling_frequency_hz)

        if trigger_mode == "on":

            self.do_task.timing.cfg_samp_clk_timing(
                rate = sampling_frequency_hz,
                active_edge = TRIGGER_POLARITY[trigger_polarity],
                sample_mode = SAMPLE_MODE[sample_mode],
                samps_per_chan = daq_samples)

            self.do_task.triggers.start_trigger.cfg_dig_edge_start_trig(
                trigger_source=f'/{self.id}/{trigger_port}',
                trigger_edge=TRIGGER_EDGE[trigger_polarity])

            self.do_task.triggers.start_trigger.retriggerable = RETRIGGERABLE_MODE[retriggerable]

        if trigger_mode == "off":

            self.do_task.timing.cfg_samp_clk_timing(
                rate = sampling_frequency,
                sample_mode = SAMPLE_MODE[sample_mode],
                samps_per_chan = int((period_time_ms/1000)/sampling_frequency_hz))

        self.do_task.do_line_states_done_state = Level.LOW
        self.do_task.do_line_states_paused_state = Level.LOW

        self.tasks.append(self.do_task)

    def generate_do_waveforms(self, do_task: dict, wavelength: str):

        period_time_ms = do_task['timing']['period_time_ms']
        if period_time_ms < 0:
            raise ValueError("Period time must be >0 ms")

        rest_time_ms = do_task['timing']['rest_time_ms']
        if rest_time_ms < 0:
            raise ValueError("Period time must be >0 ms")

        sampling_frequency_hz = do_task['timing']['sampling_frequency_hz']
        if sampling_frequency_hz < 0 or sampling_frequency_hz > self.max_do_rate:
            raise ValueError(f"Sampling frequency must be >0 Hz and \
                             <{self.max_do_rate} Hz!")

        for channel in do_task['ports']:
            # load waveform and variables
            port = channel['port']
            name = channel['name']
            waveform = channel['waveform']
            valid = DO_WAVEFORMS
            if waveform not in DO_WAVEFORMS:
                raise ValueError("waveform must be one of %r." % valid)
            if waveform == 'square wave':
                try:
                    start_time_ms = channel['parameters']['start_time_ms']['channels'][wavelength]
                    if start_time_ms > period_time_ms:
                        raise ValueError("start time must be < period time")
                    end_time_ms = channel['parameters']['end_time_ms']['channels'][wavelength]
                    if end_time_ms > period_time_ms or end_time_ms < start_time_ms:
                        raise ValueError("end time must be < period time and > start time")
                except:
                    raise ValueError("missing input parameter for square wave")
                self.do_waveforms[f'{port}: {name}'] = self.square_wave(sampling_frequency_hz,
                                                     period_time_ms,
                                                     start_time_ms,
                                                     end_time_ms,
                                                     rest_time_ms,
                                                     5.0,
                                                     0.0
                                                     )

        self.do_sampling_frequency_hz = sampling_frequency_hz
        self.do_total_time_ms = period_time_ms + rest_time_ms

    def write_do_waveforms(self):

        do_voltages = list()
        for waveform in self.do_waveforms:
            do_voltages.append(self.do_waveforms[waveform])
        do_voltages = numpy.array(do_voltages)

        # unreserve buffer
        self.do_task.control(TaskMode.TASK_UNRESERVE)
        # sets buffer to length of voltages
        self.do_task.out_stream.output_buf_size = len(do_voltages[0])
        self.do_task.control(TaskMode.TASK_COMMIT)

        self.do_task.write(numpy.array(do_voltages).astype(bool))

    def sawtooth(self,
                 sampling_frequency_hz: float,
                 period_time_ms: float,
                 start_time_ms: float,
                 end_time_ms: float,
                 rest_time_ms: float,
                 amplitude_volts: float,
                 offset_volts: float,
                 cutoff_frequency_hz: float
                 ):

        time_samples_ms = numpy.linspace(0, 2*numpy.pi, int(((period_time_ms-start_time_ms)/1000)*sampling_frequency_hz))
        waveform = offset_volts + amplitude_volts*signal.sawtooth(t=time_samples_ms,
                                                                  width=end_time_ms/period_time_ms)

        # add in delay
        delay_samples = int((start_time_ms/1000)*sampling_frequency_hz)
        waveform = numpy.pad(array=waveform,
                             pad_width=(delay_samples, 0),
                             mode='constant',
                             constant_values=(offset_volts-amplitude_volts)
                             )

        # add in rest
        rest_samples = int((rest_time_ms/1000)*sampling_frequency_hz)
        waveform = numpy.pad(array=waveform,
                             pad_width=(0, rest_samples),
                             mode='constant',
                             constant_values=(offset_volts-amplitude_volts)
                             )

        # bessel filter order 6, cutoff frequency is normalied from 0-1 by nyquist frequency
        b,a = signal.bessel(6, cutoff_frequency_hz/(sampling_frequency_hz/2), btype='low')

        # pad before filtering with last value
        padding = int(2/(cutoff_frequency_hz/(sampling_frequency_hz)))
        if padding > 0:
            # waveform = numpy.hstack([waveform[:padding], waveform, waveform[-padding:]])
            waveform = numpy.pad(array=waveform,
                             pad_width=(padding, padding),
                             mode='constant',
                             constant_values=(offset_volts-amplitude_volts)
                             )
        
        # bi-directional filtering
        waveform = signal.lfilter(b, a, signal.lfilter(b, a, waveform)[::-1])[::-1]
        
        if padding > 0:
            waveform = waveform[padding:-padding]

        return waveform

    def square_wave(self,
                 sampling_frequency_hz: float,
                 period_time_ms: float,
                 start_time_ms: float,
                 end_time_ms: float,
                 rest_time_ms: float,
                 max_volts: float,
                 min_volts: float
                 ):

        time_samples = int(((period_time_ms+rest_time_ms)/1000)*sampling_frequency_hz)
        start_sample = int((start_time_ms/1000)*sampling_frequency_hz)
        end_sample = int((end_time_ms/1000)*sampling_frequency_hz)
        waveform = numpy.zeros(time_samples) + min_volts
        waveform[start_sample:end_sample] = max_volts

        return waveform

    def triangle_wave(self,
                 sampling_frequency_hz: float,
                 period_time_ms: float,
                 start_time_ms: float,
                 end_time_ms: float,
                 rest_time_ms: float,
                 amplitude_volts: float,
                 offset_volts: float,
                 cutoff_frequency_hz: float
                 ):

        # sawtooth with end time in center of waveform
        waveform = self.sawtooth(sampling_frequency_hz,
                                 period_time_ms,
                                 start_time_ms,
                                 (period_time_ms - start_time_ms)/2,
                                 rest_time_ms,
                                 amplitude_volts,
                                 offset_volts,
                                 cutoff_frequency_hz
                                )

        return waveform

    def plot_waveforms_to_pdf(self):

        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['font.weight'] = 'light'
        plt.rcParams["figure.figsize"] = [6, 4]
        plt.rcParams['lines.linewidth'] = 1

        ax = plt.axes()

        if self.ao_waveforms:
            time_ms = numpy.linspace(0,
                self.ao_total_time_ms,
                int(self.ao_total_time_ms/1000*self.ao_sampling_frequency_hz))
            for waveform in self.ao_waveforms:
                plt.plot(time_ms, self.ao_waveforms[waveform], label=waveform)
        if self.do_waveforms:
            time_ms = numpy.linspace(0,
                self.do_total_time_ms,
                int(self.do_total_time_ms/1000*self.do_sampling_frequency_hz))
            for waveform in self.do_waveforms:
                plt.plot(time_ms, self.do_waveforms[waveform], label=waveform)

        plt.axis([0, numpy.max([self.ao_total_time_ms, self.do_total_time_ms]), -0.2, 5.2])
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.spines[['right', 'top']].set_visible(False)
        ax.set_xlabel("time, ms")
        ax.set_ylabel("amplitude, volts")
        ax.legend(loc="upper right", fontsize=10, edgecolor=None)
        ax.tick_params(which='major', direction='out', length=8, width=0.75)
        ax.tick_params(which='minor', length=4)
        plt.savefig('waveforms.pdf', bbox_inches='tight')

    def start_all(self):

        for task in self.tasks:
            task.start()

    def stop_all(self):

        for task in self.tasks:
            task.stop()

    def close_all(self):
        
        for task in self.tasks:
            task.close()

    def restart_all(self):

        for task in self.tasks:
            task.stop()
        for task in self.tasks:
            task.start()

    def wait_until_done_all(self, timeout=1.0):

        for task in self.tasks:
            task.wait_until_done(timeout)

    def is_finished_all(self):

        for task in self.tasks:
            if not task.is_task_done():
                return False
            else:
                pass
        return True