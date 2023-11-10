from abc import ABC, abstractmethod


class Laser(ABC):

    @abstractmethod
    @property
    def current_setpoint(self):
        pass

    @abstractmethod
    @property
    def power_setpoint(self):
        pass

    @abstractmethod
    @property
    def max_power(self):
        pass

    @abstractmethod
    @property
    def max_current(self):
        pass
    @abstractmethod
    @property
    def digital_modulation(self):
        pass

    @abstractmethod
    @property
    def analog_modulation(self):
        pass

    @abstractmethod
    @property
    def temperature(self):
        pass

    @abstractmethod
    @property
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