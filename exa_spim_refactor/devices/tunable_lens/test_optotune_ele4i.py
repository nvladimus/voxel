import optotune_ele4i

etl = optotune_ele4i.TunableLens(port='COM4')
print(etl.mode)
etl.mode = 'internal'
print(etl.mode)
etl.mode = 'external'
print(etl.mode)
print(etl.temperature)
print(etl.id)