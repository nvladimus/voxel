from voxel.instrument.devices.tunable_lens import TunableLens

etl = TunableLens(port='COM4')
print(etl.mode)
etl.mode = 'internal'
print(etl.mode)
etl.mode = 'external'
print(etl.mode)
print(etl.temperature)
print(etl.name)