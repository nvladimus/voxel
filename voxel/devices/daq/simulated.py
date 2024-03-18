import logging
import numpy
import matplotlib.pyplot as plt
from voxel.devices.daq.base import BaseDAQ
from matplotlib.ticker import AutoMinorLocator
from scipy import signal

# lets just simulate the PCIe-6738
AO_PHYSICAL_CHANS = [
    'ao0',
    'ao1',
    'ao2',
    'ao3',
    'ao4',
    'ao5',
    'ao6',
    'ao7',
    'ao8',
    'ao9',
    'ao10',
    'ao11',
    'ao12',
    'ao13',
    'ao14',
    'ao15',
    'ao16',
    'ao17',
    'ao18',
    'ao19',
    'ao20',
    'ao21',
    'ao22',
    'ao23',
    'ao24',
    'ao25',
    'ao26',
    'ao27',
    'ao28',
    'ao29',
    'ao30',
    'ao31',
]

CO_PHYSICAL_CHANS = [
    'ctr0',
    'ctr1'
]

DO_PHYSICAL_CHANS = [
    'port0',
    'port1'
]

DIO_PORTS = [
    'PFI0',
    'PFI1'
]

DO_WAVEFORMS = [
    'square wave'
]

AO_WAVEFORMS = [
    'square wave',
    'sawtooth',
    'triangle wave'
]

class DAQ(BaseDAQ):

    def __init__(self, dev: str):

        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)       
        self.id = dev
        self.ao_physical_chans = list()
        self.co_physical_chans = list()
        self.do_physical_chans = list()
        self.dio_ports = list()
        for channel in AO_PHYSICAL_CHANS:
            self.ao_physical_chans.append(f'{self.id}/{channel}')
        for channel in CO_PHYSICAL_CHANS:
            self.co_physical_chans.append(f'{self.id}/{channel}')
        for channel in DO_PHYSICAL_CHANS:
            self.do_physical_chans.append(f'{self.id}/{channel}')
        for port in DIO_PORTS:
            self.dio_ports.append(f'{self.id}/{port}')
        self.max_ao_rate = 350e3
        self.min_ao_rate = 1e3
        self.max_do_rate = 350e3
        self.max_ao_volts = 10
        self.min_ao_volts = -10
        self.log.info('resetting nidaq')
        self.tasks = list()
        self.task_time_s = dict()
        self.ao_waveforms = dict()
        self.do_waveforms = dict()

    def add_task(self, task: dict, task_type: str, pulse_count = None):

        # check task type
        if task_type not in ['ao', 'co', 'do']:
            raise ValueError(f"{task_type} must be one of {['ao', 'co', 'do']}")

        timing = task['timing']

        for k, v in timing.items():
            global_var = globals().get(k.upper(),{})
            valid = list(global_var.keys()) if type(global_var) == dict else global_var
            if v not in valid and valid != []:
                raise ValueError(f"{k} must be one of {valid}")

        channel_options = {'ao':self.ao_physical_chans, 'do':self.do_physical_chans, 'co':self.co_physical_chans}

        if task_type in ['ao', 'do']:
            self._timing_checks(task, task_type)

            trigger_port = timing['trigger_port']
            if f"{self.id}/{trigger_port}" not in self.dio_ports:
                raise ValueError("trigger port must be one of %r." % self.dio_ports)

            for channel_port in task['ports'].keys():
                # add channel to task
                if f"{self.id}/{channel_port}" not in channel_options[task_type]:
                    raise ValueError(f"{task_type} number must be one of {channel_options[task_type]}")
                physical_name = f"/{self.id}/{channel_port}"

            total_time_ms = timing['period_time_ms'] + timing['rest_time_ms']
            daq_samples = int(((total_time_ms)/1000)*timing['sampling_frequency_hz'])

            # store the total task time
            self.task_time_s[task['name']] = total_time_ms/1000

        else:   # co channel
            if f"{self.id}/{ timing['output_port']}" not in self.dio_ports:
                raise ValueError("output port must be one of %r." % self.dio_ports)

            if timing['frequency_hz'] < 0:
                raise ValueError(f"frequency must be >0 Hz")

            for channel in task['counters']:
                channel_number = channel['counter']
                if f"{self.id}/{channel_number}" not in self.co_physical_chans:
                    raise ValueError("co number must be one of %r." % self.co_physical_chans)
                physical_name = f"/{self.id}/{channel_number}"
            # store the total task time
            self.task_time_s[task['name']] = 1/timing['frequency_hz']

    def _timing_checks(self, task: dict, task_type: str):
        """Check period time, rest time, and sample frequency"""

        timing = task['timing']

        period_time_ms = timing['period_time_ms']
        if period_time_ms < 0:
            raise ValueError("Period time must be >0 ms")

        rest_time_ms = timing['rest_time_ms']
        if rest_time_ms < 0:
            raise ValueError("Period time must be >0 ms")

        sampling_frequency_hz = timing['sampling_frequency_hz']
        if sampling_frequency_hz < getattr(self, f"min_{task_type}_rate", 0) or sampling_frequency_hz > \
                getattr(self, f"max_{task_type}_rate"):
            raise ValueError(f"Sampling frequency must be > {getattr(self, f'{task_type}_min_rate', 0)} Hz and \
                                         <{getattr(self, f'{task_type}_max_rate')} Hz!")

    def generate_waveforms(self, task: dict, task_type: str, wavelength: str):

        # check task type
        if task_type not in ['ao', 'do']:
            raise ValueError(f"{task_type} must be one of {['ao', 'do']}")

        self._timing_checks(task, task_type)

        timing = task['timing']

        waveform_attribute = getattr(self, f"{task_type}_waveforms")
        for channel in task['ports']:
            # load waveform and variables
            port = channel['port']
            name = channel['name']
            device_min_volts = channel.get('device_min_volts', 0)
            device_max_volts = channel.get('device_max_volts', 5)
            waveform = channel['waveform']

            valid = globals().get(f"{task_type.upper()}_WAVEFORMS")
            if waveform not in valid:
                raise ValueError("waveform must be one of %r." % valid)

            start_time_ms = channel['parameters']['start_time_ms']['channels'][wavelength]
            if start_time_ms > timing['period_time_ms']:
                raise ValueError("start time must be < period time")
            end_time_ms = channel['parameters']['end_time_ms']['channels'][wavelength]
            if end_time_ms > timing['period_time_ms'] or end_time_ms < start_time_ms:
                raise ValueError("end time must be < period time and > start time")

            if waveform == 'square wave':
                try:
                    max_volts = channel['parameters']['max_volts']['channels'][wavelength] if task_type == 'ao' else 5
                    if max_volts > self.max_ao_volts:
                        raise ValueError(f"max volts must be < {self.max_ao_volts} volts")
                    min_volts = channel['parameters']['min_volts']['channels'][wavelength] if task_type == 'ao' else 0
                    if min_volts < self.min_ao_volts:
                        raise ValueError(f"min volts must be > {self.min_ao_volts} volts")
                except AttributeError:
                    raise ValueError("missing input parameter for square wave")
                voltages = self.square_wave(timing['sampling_frequency_hz'],
                                             timing['period_time_ms'],
                                             start_time_ms,
                                             end_time_ms,
                                             timing['rest_time_ms'],
                                             max_volts,
                                             min_volts
                                             )

            if waveform == 'sawtooth' or waveform == 'triangle wave':   # setup is same for both waves, only be ao task
                try:
                    amplitude_volts = channel['parameters']['amplitude_volts']['channels'][wavelength]
                    offset_volts = channel['parameters']['offset_volts']['channels'][wavelength]
                    if offset_volts < self.min_ao_volts or offset_volts > self.max_ao_volts:
                        raise ValueError(f"min volts must be > {self.min_ao_volts} volts and < {self.max_ao_volts} volts")
                    cutoff_frequency_hz = channel['parameters']['cutoff_frequency_hz']['channels'][wavelength]
                    if cutoff_frequency_hz < 0:
                        raise ValueError(f"cutoff frequnecy must be > 0 Hz")
                except AttributeError:
                    raise ValueError(f"missing input parameter for {waveform}")

                waveform_function = getattr(self, waveform.replace(' ', '_'))
                voltages = waveform_function(timing['sampling_frequency_hz'],
                                         timing['period_time_ms'],
                                         start_time_ms,
                                         end_time_ms,
                                         timing['rest_time_ms'],
                                         amplitude_volts,
                                         offset_volts,
                                         cutoff_frequency_hz
                                        )


            # sanity check voltages for ni card range
            max = getattr(self, 'ao_max_volts', 5)
            min = getattr(self, 'ao_min_volts', 0)
            if numpy.max(voltages[:]) > max or numpy.min(voltages[:]) < min:
                raise ValueError(f"voltages are out of ni card range [{max}, {min}] volts")

            # sanity check voltages for device range
            if numpy.max(voltages[:]) > device_max_volts or numpy.min(voltages[:]) < device_min_volts:
                raise ValueError(f"voltages are out of device range [{device_min_volts}, {device_max_volts}] volts")

            # store 1d voltage array into 2d waveform array

            waveform_attribute[f"{port}: {name}"] = voltages

        # store these values as properties for plotting purposes
        setattr(self, f"{task_type}_sampling_frequency_hz", timing['sampling_frequency_hz'])
        setattr(self, f"{task_type}_total_time_ms", timing['period_time_ms'] + timing['rest_time_ms'])


    def write_ao_waveforms(self):
        pass

    def write_do_waveforms(self):
        pass
        
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

    def _rereserve_buffer(self, buf_len):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        pass

    def restart(self):
        pass

    def wait_until_done_all(self, timeout=1.0):
        pass

    def is_finished_all(self):
        pass