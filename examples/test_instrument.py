from exa_spim_refactor.instrument import Instrument

instrument = Instrument('test_instrument.yaml')
instrument.construct()
print(instrument.cameras)
print(instrument.tiling_stages)
print(instrument.scanning_stages)
print(instrument.filter_wheels)
print(instrument.daqs)

for stage_id in instrument.tiling_stages:
    print(id(instrument.tiling_stages[stage_id].tigerbox))

for stage_id in instrument.scanning_stages:
    print(id(instrument.scanning_stages[stage_id].tigerbox))

for filter_wheel_id in instrument.filter_wheels:
    print(id(instrument.filter_wheels[filter_wheel_id].tigerbox))