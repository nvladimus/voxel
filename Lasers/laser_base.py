from abc import ABC, abstractmethod


class Laser(ABC):

    @abstractmethod
    @property
    def setpoint(self):
        pass

    @abstractmethod
    @property
    def max_setpoint(self):
        pass

    @abstractmethod
    @property
    def modulation_mode(self):
        pass

    @abstractmethod
    def status(self):
        pass

    @abstractmethod
    def disable_cdrh(self):
        pass

    @abstractmethod
    def enable(self):
        pass

    @abstractmethod
    def disable(self):
        pass