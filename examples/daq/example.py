import time

from matplotlib import pyplot as plt

from voxel.devices.nidaq.channel import DAQWaveform
from voxel.devices.nidaq.ni import VoxelNIDAQ
from voxel.devices.nidaq.task import DAQTask, DAQTaskType, DAQTaskChannel

USE_SIMULATED = False
DEVICE_NAME = 'Dev1'

# Analog output channels connected to scope
CH1 = 'ao0'
CH2 = 'ao4'
CH3 = 'ao8'
CH4 = 'ao12'

if __name__ == '__main__':
    daq = VoxelNIDAQ(id="example-daq", conn="Dev1", simulated=USE_SIMULATED)

    # Create a task
    ao_task = DAQTask(
        name="AO_Task",
        task_type=DAQTaskType.AO,
        sampling_frequency_hz=350e3,
        period_time_ms=10,
        rest_time_ms=0,
        daq=daq
    )

    # Create channels
    square_channel = DAQTaskChannel(
        name="Square",
        waveform_type=DAQWaveform.SQUARE,
        center_volts=0,
        amplitude_volts=5,
        cut_off_frequency_hz=1000,
        start_time_ms=0,
        end_time_ms=5
    )

    triangle_channel = DAQTaskChannel(
        name="Triangle",
        waveform_type=DAQWaveform.TRIANGLE,
        center_volts=0,
        amplitude_volts=2.5,
        cut_off_frequency_hz=1000,
        start_time_ms=0,
        end_time_ms=5
    )

    delayed_square_channel = DAQTaskChannel(
        name="Delayed Square",
        waveform_type=DAQWaveform.SQUARE,
        center_volts=0,
        amplitude_volts=2.5,
        cut_off_frequency_hz=1000,
        start_time_ms=2.5,
        end_time_ms=7.5
    )
    sawtooth_channel = DAQTaskChannel(
        name="Sawtooth",
        waveform_type=DAQWaveform.TRIANGLE,
        center_volts=0,
        amplitude_volts=2.5,
        cut_off_frequency_hz=1000,
        start_time_ms=0,
        end_time_ms=10
    )

    # Add channels to the task
    ao_task.add_channel(square_channel, port=CH1)
    ao_task.add_channel(triangle_channel, port=CH2)

    # Simulated has only 2 channels
    if not USE_SIMULATED:
        ao_task.add_channel(delayed_square_channel, port=CH3)
        ao_task.add_channel(sawtooth_channel, port=CH4)

    plt.ion()
    ao_task.plot_waveforms(num_cycles=3)

    try:
        import sys

        start_time = time.time()
        ao_task.start()
        while True:
            time.sleep(1)
            elapsed_time = time.time() - start_time
            sys.stdout.write(f"\rRunning for {elapsed_time:.2f} seconds...")
            sys.stdout.flush()
            plt.pause(0.1)
    except KeyboardInterrupt:
        ao_task.stop()
    finally:
        daq.close()
        plt.ioff()
