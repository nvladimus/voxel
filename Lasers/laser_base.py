from abc import ABC, abstractmethod


class Laser(ABC):

    @property
    @abstractmethod
    def power_setpoint(self):
        pass

    @property
    @abstractmethod
    def max_power(self):
        pass

    @property
    @abstractmethod
    def digital_modulation(self):
        pass

    @property
    @abstractmethod
    def analog_modulation(self):
        pass

    @property
    @abstractmethod
    def temperature(self):
        pass

    @property
    @abstractmethod
    def external_control_mode(self):
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