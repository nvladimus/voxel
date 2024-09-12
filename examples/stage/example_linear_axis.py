from dataclasses import dataclass
from typing import Optional

from voxel.instrument.devices import VoxelLinearAxis


# max speed = 1.92 mm/s

@dataclass
class VoxelStage:
    x: VoxelLinearAxis
    y: VoxelLinearAxis
    z: VoxelLinearAxis

    def __repr__(self):
        return (
            f"x: \n{self.x}--- \n"
            f"y: \n{self.y}--- \n"
            f"z: \n{self.z}--- \n"
        )

    @property
    def position_mm(self):
        return self.x.position_mm, self.y.position_mm, self.z.position_mm

    @position_mm.setter
    def position_mm(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None):
        if x is not None:
            self.x.position_mm = x
        if y is not None:
            self.y.position_mm = y
        if z is not None:
            self.z.position_mm = z

    @property
    def limits_mm(self):
        return (
            (self.x.lower_limit_mm, self.x.upper_limit_mm),
            (self.y.lower_limit_mm, self.y.upper_limit_mm),
            (self.z.lower_limit_mm, self.z.upper_limit_mm)
        )

    @property
    def speed_mm_s(self):
        return self.x.speed_mm_s, self.y.speed_mm_s, self.z.speed_mm_s

    def go_to_origin(self):
        self.x.go_to_origin()
        self.y.go_to_origin()
        self.z.go_to_origin()

    def zero_in_place(self):
        self.x.zero_in_place()
        self.y.zero_in_place()
        self.z.zero_in_place()


def sweep_axis(axis: VoxelLinearAxis, step: int = 10):
    axis.speed_mm_s = 1.9
    axis.position_mm = int(axis.lower_limit_mm)
    print(f"Sweeping axis {axis.name}")
    print(axis)
    for pos in range(int(axis.lower_limit_mm / 5), int(axis.upper_limit_mm / 5), step // 10):
        axis.position_mm = pos
        axis.await_movement()
        print(axis.position_mm)

    print(axis)


if __name__ == '__main__':
    from voxel.instrument.hubs.tigerbox import ASITigerBox
    from voxel.instrument.devices import LinearAxisDimension
    from voxel.instrument.devices import ASITigerLinearAxis

    PORT = 'COM3'
    controller = ASITigerBox(port=PORT)

    # print('Hardware axes: ', controller.box.ordered_axes)

    x_axis = ASITigerLinearAxis('x-axis', 'x', LinearAxisDimension.X, controller)
    y_axis = ASITigerLinearAxis('y-axis', 'y', LinearAxisDimension.Y, controller)
    scanning_axis = ASITigerLinearAxis('step-shoot-axis', 'z', LinearAxisDimension.Z, controller)
    stage = VoxelStage(x_axis, y_axis, scanning_axis)
    n_axis = ASITigerLinearAxis('objective-axis', 't', LinearAxisDimension.N, controller)

    x_axis.speed_mm_s = 2
    x_axis.go_to_origin()
    x_axis.await_movement()

    # x_axis.speed_mm_s = 0.5
    # x_axis.acceleration_ms = 1
    # print(x_axis)
    #
    # start_time_ms = time.perf_counter()
    # x_axis.position_mm += 1
    # x_axis.await_move()
    # print(f"Time taken: {time.perf_counter() - start_time_ms}")
    # print(x_axis)
    #
    # start_time_ms = time.perf_counter()
    # x_axis.position_mm = x_axis.upper_limit_mm
    # x_axis.await_move()
    # print(f"Time taken: {time.perf_counter() - start_time_ms}")
    # print(x_axis)

    print(controller.joystick_mapping)
    print(controller.axis_map)

    # sweep_axis(x_axis)
    # for axis in (x_axis, y_axis, scanning_axis, n_axis):
    #     sweep_axis(axis)

    # print(f"Controller Axis Map: {controller.axis_map}")
    # print(f"Controller Dimensions: {controller.dimensions_map}")

    # print("\nFocusing axis")
    # print(n_axis)

    # n_axis.home_position_mm = n_axis.lower_limit_mm
    # print(n_axis)
    #
    # n_axis.position_mm = n_axis.upper_limit_mm
    # n_axis.position_mm -= 100
    # n_axis.home()
    # print(n_axis)

    # x_axis.position_mm = 0
    # print(x_axis)

    # x_axis.position_mm = (x_axis.lower_limit_mm + x_axis.upper_limit_mm) // 2
    # x_axis.zero_in_place()
    # x_axis.home_position_mm = x_axis.position_mm
    # print(x_axis)

    # x_axis.position_mm = x_axis.upper_limit_mm + 100000
    # print(x_axis)
    #
    # y_axis.position_mm = y_axis.upper_limit_mm + 100000
    # print(y_axis)
    #
    # scanning_axis.position_mm = scanning_axis.upper_limit_mm + 100000
    # print(scanning_axis)

    # print("\nSpacial stage")
    # stage.position_mm = 10, 20, 30
    # print(stage)
    #
    # print("\nHome the stage")
    # stage.home()
    # print(stage)
    #
    # x_limits, y_limits, z_limits = stage.limits_mm
    #
    # print("\nSet the stage to lower limits")
    # stage.position_mm = x_limits[0], y_limits[0], z_limits[0]
    # print(stage)
    #
    # print("\nSet the stage to upper limits")
    # stage.position_mm = x_limits[1], y_limits[1], z_limits[1]
    # print(stage)
