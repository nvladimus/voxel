from pprint import pprint
from time import sleep

import numpy as np

from voxel.core.instrument.daq.daq import VoxelDaq
from voxel.core.instrument.daq.tasks.clockgen import ClkGenTask
from voxel.core.instrument.daq.tasks.dc_control import DCControl
from voxel.core.instrument.daq.tasks.wavegen import WaveGenTask
from voxel.core.utils.logging import setup_logging

setup_logging(log_level="INFO")


def plot_waveforms(task: WaveGenTask):
    from matplotlib import pyplot as plt

    _, ax = plt.subplots()
    for _, channel in task.channels.items():
        channel.wave.plot(ax=ax)

    plt.ion()
    plt.show()
    plt.pause(0.1)


def run_task(task: WaveGenTask | ClkGenTask, duration: int = 30) -> None:
    with task:
        sleep(duration)


if __name__ == "__main__":

    # channels
    # test1 -> ao20 (oscilloscope 1)
    # galvo -> ao0 (oscilloscope 2)
    # test2 -> ao4 (ad2 1)
    # clk   -> pf10 (ad2 2)

    daq = VoxelDaq("Dev1")
    pprint(daq)

    period_ms = 100
    freq_hz = 1 / (period_ms / 1000)

    clk = ClkGenTask(name="clk", daq=daq, out_pin="PFI0", freq_hz=freq_hz)
    task = WaveGenTask(name="TestTask", daq=daq, sampling_rate_hz=1e6, period_ms=period_ms, trigger=clk)
    test1 = task.add_ao_channel(name="test1-ao20-ch1", pin="ao20")
    galvo = task.add_ao_channel(name="galvo-ch2", pin="ao0")
    test2 = task.add_ao_channel(name="test2-ad2-1", pin="ao4")
    task.write()
    with task:
        with clk:
            sleep(2)

    clk.close()
    task.close()

    # sleep(1)

    dc_task = DCControl(name="dc_task", daq=daq, pin="ao4")  # can reuse since test2 is closed

    voltages = np.linspace(daq.min_ao_voltage / 2, daq.max_ao_voltage / 2, 50)
    # voltages = np.concatenate((voltages, voltages[::-1]))

    for voltage in voltages:
        dc_task.voltage = voltage
        sleep(0.05)

    # dc_task.close()
    daq.clean_up()
