from abc import ABC, abstractmethod


class Laser(ABC):

    @property
    @abstractmethod
    def power_setpoint_mw(self):
        pass

    @property
    @abstractmethod
    def max_power_mw(self):
        pass

    @property
    @abstractmethod
    def modulation_mode(self):
        pass

    @property
    @abstractmethod
    def temperature(self):
        pass

    @abstractmethod
    def status(self):
        pass

    @abstractmethod
    def cdrh(self):
        pass

    @abstractmethod
    def enable(self):
        pass

    @abstractmethod
    def disable(self):
        pass