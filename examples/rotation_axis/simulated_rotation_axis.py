# Example usage
from voxel.instrument.drivers.rotation_axis.simulated import SimulatedRotationAxis
from voxel.utils.logging import setup_logging

if __name__ == "__main__":
    setup_logging(log_level="DEBUG")
    axis = SimulatedRotationAxis("test_axis")

    print("Moving to 90 degrees...")
    axis.position_deg = 90
    axis.wait_until_stopped()
    print(f"Reached position: {axis.position_deg:.2f}")

    print("Changing speed and moving to 180 degrees...")
    axis.speed_deg_s = 20
    axis.position_deg = 180
    axis.wait_until_stopped()
    print(f"Reached position: {axis.position_deg:.2f}")

    axis.close()
    print("Device closed.")
