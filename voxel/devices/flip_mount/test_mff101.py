from voxel.devices.flip_mount.thorlabs_mff101 import FlipMount

positions = {
    'A': 0,
    'B': 1
}
serial_num = 37007737
flip_mount = FlipMount(serial_num, positions)
print(flip_mount.switch_time_ms)
flip_mount.switch_time_ms = 2000
print(flip_mount.switch_time_ms)
print(flip_mount.position)
flip_mount.position = 'B'
print(flip_mount.position)
flip_mount.position = 'A'
print(flip_mount.position)