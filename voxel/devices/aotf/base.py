from abc import abstractmethod

from voxel.devices import VoxelDevice


class VoxelAOTF(VoxelDevice):

    def __init__(self, id):
        super().__init__(id)

    @abstractmethod
    def enable_all(self):
        pass

    @abstractmethod
    def disable_all(self):
        pass

    @abstractmethod
    @property
    def frequency_hz(self):
        pass

    @abstractmethod
    def set_frequency_hz(self, channel: int, frequency_hz: dict):
        pass

    @abstractmethod
    @property
    def power_dbm(self):
        pass

    @abstractmethod
    def set_power_dbm(self, channel: int, power_dbm: dict):
        pass

    @abstractmethod
    @property
    def blanking_mode(self):
        pass

    @abstractmethod
    @blanking_mode.setter
    def blanking_mode(self, mode: str):
        pass

    @abstractmethod
    @property
    def input_mode(self):
        pass

    @abstractmethod
    @input_mode.setter
    def input_mode(self, modes: dict):
        pass
