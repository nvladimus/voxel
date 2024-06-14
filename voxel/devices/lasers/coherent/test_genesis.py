from voxel.devices.lasers import GenesisLaser

TEST_LASER = {
    "id": "test_laser",
    "conn": "A700467EP203"
}

if __name__ == "__main__":
    laser = GenesisLaser(TEST_LASER["id"], TEST_LASER["conn"])
    print(laser.power_mw)
    print(laser.power_setpoint_mw)
    laser.close()
