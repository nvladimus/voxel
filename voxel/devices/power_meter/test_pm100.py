from voxel.devices.power_meter.thorlabs_pm100 import PowerMeter

serial_num = 'P0008860'
power_meter = PowerMeter(serial_num)
print(power_meter.power_mw)
print(power_meter.wavelength_nm)
power_meter.wavelength_nm = 500
print(power_meter.wavelength_nm)
print(power_meter.sensor_mode)
power_meter.sensor_mode = 'power'
print(power_meter.sensor_mode)