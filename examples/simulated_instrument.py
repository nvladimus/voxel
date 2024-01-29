from exa_spim_refactor.instrument import Instrument


instrument = Instrument('simulated_instrument.yaml')
instrument.construct()
print(instrument.cameras)
print(instrument.tiling_stages)
print(instrument.scanning_stages)
print(instrument.filter_wheels)
print(instrument.daqs)