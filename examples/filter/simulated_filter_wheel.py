# Usage example
from voxel.devices.filter import SimulatedFilterWheel, SimulatedFilter, VoxelDeviceError

if __name__ == "__main__":
    import logging


    def setup_simulated_filter_system():
        wheel = SimulatedFilterWheel("main_wheel", "simulated_wheel_id")

        red_filter = SimulatedFilter("red_filter", "red", wheel, 0)
        green_filter = SimulatedFilter("green_filter", "green", wheel, 1)
        blue_filter = SimulatedFilter("blue_filter", "blue", wheel, 2)

        return red_filter, green_filter, blue_filter, wheel


    def print_active_filter(w: SimulatedFilterWheel):
        w.log.info(f"Active filter: {w.current_filter or 'None'}")


    logging.basicConfig(level=logging.INFO)

    red, green, blue, wheel = setup_simulated_filter_system()
    print_active_filter(wheel)

    red.enable()
    print_active_filter(wheel)
    red.disable()

    green.enable()
    print_active_filter(wheel)
    green.disable()

    red.disable()
    print_active_filter(wheel)

    blue.enable()
    print_active_filter(wheel)

    blue.close()
    print_active_filter(wheel)

    try:
        red.enable()
    except VoxelDeviceError as e:
        print(e)
    print_active_filter(wheel)

    try:
        red.close()
    except VoxelDeviceError as e:
        print(e)
    print_active_filter(wheel)
