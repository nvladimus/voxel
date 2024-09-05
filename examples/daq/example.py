from voxel.devices.nidaq.channel import DAQWaveform
from voxel.devices.nidaq.ni import VoxelNIDAQ
from voxel.devices.nidaq.task import DAQTask, DAQTaskType, DAQTaskChannel

DEVICE_NAME = 'Dev1'
USE_SIMULATED = False

if __name__ == '__main__':
    daq = VoxelNIDAQ(id="example-daq", conn="Dev1", simulated=USE_SIMULATED)

    # Create a task
    ao_task = DAQTask(
        name="AO_Task",
        task_type=DAQTaskType.AO,
        sampling_frequency_hz=350e3,
        period_time_ms=10,
        rest_time_ms=2,
        daq=daq
    )

    # Create channels
    square_channel = DAQTaskChannel(
        name="Square",
        port="ao0",
        waveform_type=DAQWaveform.SQUARE,
        center_volts=0,
        amplitude_volts=2.5,
        cut_off_frequency_hz=1000,
        start_time_ms=0,
        end_time_ms=5
    )

    triangle_channel = DAQTaskChannel(
        name="Triangle",
        port="ao1",
        waveform_type=DAQWaveform.TRIANGLE,
        center_volts=0,
        amplitude_volts=2.5,
        cut_off_frequency_hz=1000,
        start_time_ms=0,
        end_time_ms=5
    )

    # Add channels to the task
    ao_task.add_channel(square_channel)
    ao_task.add_channel(triangle_channel)

    # Simulated has only 2 channels
    if not USE_SIMULATED:
        delayed_square_channel = DAQTaskChannel(
            name="Delayed Square",
            port="ao2",
            waveform_type=DAQWaveform.SQUARE,
            center_volts=0,
            amplitude_volts=2.5,
            cut_off_frequency_hz=1000,
            start_time_ms=2.5,
            end_time_ms=7.5
        )
        ao_task.add_channel(delayed_square_channel)

    ao_task.plot_waveforms(num_cycles=5)

    ao_task.close()
