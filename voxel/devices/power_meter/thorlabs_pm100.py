import logging
import pyvisa as visa
from pylablib.devices import Thorlabs


class PowerMeter:
    def __init__(self, id: str):
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.id = id
        # lets find the device using pyvisa
        resource_manger = visa.ResourceManager()
        resources = resource_manger.list_resources()
        try:
            for resource in resources:
                # uses the PM160 class within devices/Thorlabs/misc of pylablib
                power_meter = Thorlabs.PM160(resource)
                info = power_meter.get_device_info()
                if info['serial'] == id:
                    self.power_meter = power_meter
                    break
        except:
            self.log.debug(f'{resource} is not a valid thorabs power meter')
            raise ValueError(f'could not find power meter with id {id}')
  
    @property
    def sensor_mode(self):
        return self.power_meter.get_sensor_mode()

    @sensor_mode.setter
    def sensor_mode(self, mode: str):
        """Set the filterwheel index."""
        supported_modes = self.power_meter.get_supported_sensor_modes()
        if mode not in supported_modes:
            raise ValueError(f'Sensor mode {mode} must be one of '
                            f'{supported_modes}')

    @property
    def power_mw(self):
        return self.power_meter.get_power(sensor_mode='power')

    def close(self):
        # inherited close property from core/devio/SCPI in pylablib
        self.close()