from voxel.devices.lasers.base import BaseLaser
import logging
from voxel.devices.daq.ni import DAQ


class AOTFLaser(BaseLaser):
    """Laser controlled by nidaq. Power is a function of voltage"""

    def __init__(self, daq: DAQ, task: dict, laser_channel: str):
        """Communicate with specific LBX laser in L6CC Combiner box.

                :param daq: daq object through which the laser is controlled through
                :param task: task detailing waveform for nidaq
                :param laser_channel: channel relating to laser in task
                """

        self.log = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.task = task
        self.daq = daq
        # update daq with laser task. ASSUMING LASER IS AO CHANNEL
        self.daq.tasks['ao_task']['ports'].update(task)
        self.task = task
        self.laser_channel = laser_channel


    @property
    def power_setpoint_mw(self):
        waveform = self.task['parameters'].get

    @power_setpoint_mw.setter
    def power_setpoint_mw(self, value: float):
        self._simulated_power_setpoint_m = value

    @property
    def max_power_mw(self):
        return self._max_power_mw

    def enable(self):
        pass

    def disable(self):
        pass

    def close(self):
        pass
