from abc import abstractmethod

from voxel.devices.base import VoxelDevice


class VoxelAOTF(VoxelDevice):

    def __init__(self, id):
        super().__init__(id)

    @abstractmethod
    def enable_all(self):
        pass

    @abstractmethod
    def disable_all(self):
        pass

    @property
    @abstractmethod
    def frequency_hz(self):
        pass

    @abstractmethod
    def set_frequency_hz(self, channel: int, frequency_hz: dict):
        pass

    @property
    @abstractmethod
    def power_dbm(self):
        pass

    @abstractmethod
    def set_power_dbm(self, channel: int, power_dbm: dict):
        pass

    @property
    @abstractmethod
    def blanking_mode(self):
        pass

    @blanking_mode.setter
    @abstractmethod
    def blanking_mode(self, mode: str):
        pass

    @property
    @abstractmethod
    def input_mode(self):
        pass

    @input_mode.setter
    @abstractmethod
    def input_mode(self, modes: dict):
        pass
