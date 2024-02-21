from exa_spim_refactor.devices.stage.asi import Stage

asi_stage1 = Stage(port='COM3', instrument_axis='X', hardware_axis='X')
asi_stage2 = Stage(port='COM3', instrument_axis='Y', hardware_axis='Y')

if id(asi_stage1.tigerbox) == id(asi_stage2.tigerbox):
    print("Singleton works, both variables contain the same instance.")
else:
    print("Singleton failed, variables contain different instances.")