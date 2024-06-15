from voxel.devices.lasers import GenesisLaser

LASER1 = {
    "id": "test_laser",
    "conn": "A700467EP203"
}

LASER2 = {
    "id": "test_laser",
    "conn": "J687424BP914"
}

if __name__ == "__main__":
    laser1 = GenesisLaser(LASER1["id"], LASER1["conn"])
    laser2 = GenesisLaser(LASER2["id"], LASER2["conn"])
    for laser in [laser1, laser2]:
        print(laser.power_mw)
        print(laser.power_setpoint_mw)
        laser.close()
