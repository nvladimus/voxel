from turtle import position
from voxel.instrument.devices.linear_axis import VoxelLinearAxis
from voxel.instrument.devices.rotation_axis import VoxelRotationAxis
from voxel.utils.vec import Vec3D


class VoxelStage:
    def __init__(
        self,
        x: VoxelLinearAxis,
        y: VoxelLinearAxis,
        z: VoxelLinearAxis | None = None,
        roll: VoxelRotationAxis | None = None,
        pitch: VoxelRotationAxis | None = None,
        yaw: VoxelRotationAxis | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.roll = roll  # Rotation around the x-axis
        self.pitch = pitch  # Rotation around the y-axis
        self.yaw = yaw  # Rotation around the z-axis

    @property
    def position_mm(self) -> Vec3D:
        return Vec3D(self.x.position_mm, self.y.position_mm, self.z.position_mm or 0)

    @property
    def position_deg(self) -> Vec3D:
        return Vec3D(self.roll.position_deg or 0, self.pitch.position_deg or 0, self.yaw.position_deg or 0)

    def move_to(
        self,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
        roll: float | None = None,
        pitch: float | None = None,
        yaw: float | None = None,
    ) -> None:
        """Move stage to specified positions"""
        linear_zipped = zip([x, y, z], [self.x, self.y, self.z])

        for arg, axis in linear_zipped:
            if arg is not None and axis is not None:
                axis.position_mm = arg

        rotational_zipped = zip([roll, pitch, yaw], [self.roll, self.pitch, self.yaw])
        for arg, axis in rotational_zipped:
            if arg is not None and axis is not None:
                axis.position_rad = arg

    @property
    @property
    def limits_mm(self) -> tuple[Vec3D, Vec3D]:
        return Vec3D(self.x.lower_limit_mm, self.y.lower_limit_mm, self.z.lower_limit_mm or 0), Vec3D(
            self.x.upper_limit_mm, self.y.upper_limit_mm, self.z.upper_limit_mm or 0
        )
