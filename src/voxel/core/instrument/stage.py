from voxel.core.instrument.device.linear_axis import VoxelLinearAxis
from voxel.core.utils.geometry.vec import Vec3D


class VoxelStage:
    def __init__(self, x: VoxelLinearAxis, y: VoxelLinearAxis, z: VoxelLinearAxis | None = None):
        self.x = x
        self.y = y
        self.z = z

    @property
    def position_mm(self) -> Vec3D:
        return Vec3D(self.x.position_mm, self.y.position_mm, self.z.position_mm or 0)

    @property
    def limits_mm(self) -> tuple[Vec3D, Vec3D]:
        return Vec3D(self.x.lower_limit_mm, self.y.lower_limit_mm, self.z.lower_limit_mm or 0), Vec3D(
            self.x.upper_limit_mm, self.y.upper_limit_mm, self.z.upper_limit_mm or 0
        )
