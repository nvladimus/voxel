from voxel.devices.tunable_lens.optotune_ele4i import TunableLens

etl = TunableLens(port='COM4')
print(etl.mode)
etl.mode = 'internal'
print(etl.mode)
etl.mode = 'external'
print(etl.mode)
print(etl.temperature)
print(etl.id)