import time

from matplotlib import pyplot as plt

from voxel.instrument.daq import DAQWaveform, VoxelNIDAQ
from voxel.instrument.daq.task import DAQTask, DAQTaskType

USE_SIMULATED = False
DEVICE_NAME = "Dev1"

# Analog output channels connected to scope
CH1 = "ao0"
CH2 = "ao4"
CH3 = "ao8"
CH4 = "ao12"


def main():
    daq = VoxelNIDAQ(name="example-daq", conn="Dev1", simulated=USE_SIMULATED)

    # Create a task
    ao_task = DAQTask(
        name="AO_Task",
        task_type=DAQTaskType.AO,
        sampling_frequency_hz=350e3,
        period_time_ms=10,
        rest_time_ms=0,
        daq=daq,
    )

    # Add channels
    ao_task.add_channel(
        name="Square",
        waveform_type=DAQWaveform.SQUARE,
        center_volts=0,
        amplitude_volts=5,
        cutoff_freq_hz=1000,
        start_time_ms=0,
        end_time_ms=5,
        port=CH1,
    )

    ao_task.add_channel(
        name="Triangle",
        waveform_type=DAQWaveform.TRIANGLE,
        center_volts=0,
        amplitude_volts=2.5,
        cutoff_freq_hz=1000,
        start_time_ms=0,
        end_time_ms=5,
        port=CH2,
    )

    if not USE_SIMULATED:
        ao_task.add_channel(
            name="Delayed Square",
            waveform_type=DAQWaveform.SQUARE,
            center_volts=0,
            amplitude_volts=2.5,
            cutoff_freq_hz=1000,
            start_time_ms=2.5,
            end_time_ms=7.5,
            port=CH3,
        )

        ao_task.add_channel(
            name="Sawtooth",
            waveform_type=DAQWaveform.TRIANGLE,
            center_volts=0,
            amplitude_volts=2.5,
            cutoff_freq_hz=1000,
            start_time_ms=0,
            end_time_ms=10,
            port=CH4,
        )

    # Plot waveforms
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


if __name__ == "__main__":
    main()
