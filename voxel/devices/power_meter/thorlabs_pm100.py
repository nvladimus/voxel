import logging
import pyvisa as visa
from pylablib.devices import Thorlabs


class PowerMeter:
    def __init__(self, id: str):
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.id = id # serial number of power meter
        # lets find the device using pyvisa
        resource_manger = visa.ResourceManager()
        resources = resource_manger.list_resources()
        try:
            for resource in resources:
                # uses the PM160 class within devices/Thorlabs/misc of pylablib
                power_meter = Thorlabs.PM160(resource)
                info = power_meter.get_device_info()
                if info.serial == id:
                    self.power_meter = power_meter
                    break
        except:
            self.log.debug(f'{id} is not a valid thorabs power meter')
            raise ValueError(f'could not find power meter with id {id}')
  
    @property
    def sensor_mode(self):
        return self.power_meter.get_sensor_mode()

    @sensor_mode.setter
    def sensor_mode(self, mode: str):
        supported_modes = self.power_meter.get_supported_sensor_modes()
        if mode not in supported_modes:
            raise ValueError(f'Sensor mode {mode} must be one of '
                            f'{supported_modes}')
        self.log.info(f'sensor mode set to {mode}')

    @property
    def wavelength_nm(self):
        # convert from meter to nanometer
        return self.power_meter.get_wavelength() * 1e9
    
    @wavelength_nm.setter
    def wavelength_nm(self, wavelength_nm: float):
        # convert from meter to nanometer
        wavelength_range_nm = tuple([x * 1e9 for x in self.power_meter.get_wavelength_range()])
        if wavelength_nm < wavelength_range_nm[0] or wavelength_nm > wavelength_range_nm[1]:
            raise ValueError(f'wavelength must be between {wavelength_range_nm[0]}'
                             f'and {wavelength_range_nm[1]} nm')
        self.power_meter.set_wavelength(wavelength_nm / 1e9)
        self.log.info(f'wavelength set to {wavelength_nm} nm')

    @property
    def power_mw(self):
        # convert from watt to milliwatt
        return self.power_meter.get_power() * 1e3

    def close(self):
        # inherited close property from core/devio/SCPI in pylablib
        self.close()
        self.log.info(f'power meter {self.id} closed')