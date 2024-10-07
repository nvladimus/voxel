from dataclasses import dataclass

from voxel.utils.geometry.vec import Vec3D, Plane, Vec2D


class CuboidBoundaryError(Exception):
    def __init__(self, message: str, min_value: float, max_value: float):
        super().__init__(message)
        self.min_value = min_value
        self.max_value = max_value

    def __str__(self):
        return f"{self.args[0]} (min: {self.min_value}, max: {self.max_value})"


@dataclass
class Cuboid:
    min_corner: Vec3D
    max_corner: Vec3D

    @property
    def size(self) -> Vec3D:
        return Vec3D(
            self.max_corner.x - self.min_corner.x,
            self.max_corner.y - self.min_corner.y,
            self.max_corner.z - self.min_corner.z,
        )

    @property
    def min_x(self) -> float:
        return self.min_corner.x

    @min_x.setter
    def min_x(self, plane: Plane):
        if plane.min_corner.x > self.max_corner.x:
            raise CuboidBoundaryError(
                "min_x cannot be greater than current max_x", plane.min_corner.x, self.max_corner.x
            )
        self.min_corner.x = plane.min_corner.x

    @property
    def max_x(self) -> float:
        return self.max_corner.x

    @max_x.setter
    def max_x(self, plane: Plane):
        if plane.max_corner.x < self.min_corner.x:
            raise CuboidBoundaryError("max_x cannot be less than current min_x", self.min_corner.x, plane.max_corner.x)
        self.max_corner.x = plane.max_corner.x

    @property
    def min_y(self) -> float:
        return self.min_corner.y

    @min_y.setter
    def min_y(self, plane: Plane):
        if plane.min_corner.y > self.max_corner.y:
            raise CuboidBoundaryError(
                "min_y cannot be greater than current max_y", plane.min_corner.y, self.max_corner.y
            )
        self.min_corner.y = plane.min_corner.y

    @property
    def max_y(self) -> float:
        return self.max_corner.y

    @max_y.setter
    def max_y(self, plane: Plane):
        if plane.max_corner.y < self.min_corner.y:
            raise CuboidBoundaryError("max_y cannot be less than current min_y", self.min_corner.y, plane.max_corner.y)
        self.max_corner.y = plane.max_corner.y

    @property
    def min_z(self) -> float:
        return self.min_corner.z

    @min_z.setter
    def min_z(self, plane: Plane):
        if plane.min_corner.z > self.max_corner.z:
            raise CuboidBoundaryError(
                "min_z cannot be greater than current max_z", plane.min_corner.z, self.max_corner.z
            )
        self.min_corner.z = plane.min_corner.z

    @property
    def max_z(self) -> float:
        return self.max_corner.z

    @max_z.setter
    def max_z(self, plane: Plane):
        if plane.max_corner.z < self.min_corner.z:
            raise CuboidBoundaryError("max_z cannot be less than current min_z", self.min_corner.z, plane.max_corner.z)
        self.max_corner.z = plane.max_corner.z

    @property
    def pos(self) -> Vec3D:
        return self.min_corner

    @property
    def center(self) -> Vec3D:
        return Vec3D(
            (self.min_corner.x + self.max_corner.x) / 2,
            (self.min_corner.y + self.max_corner.y) / 2,
            (self.min_corner.z + self.max_corner.z) / 2,
        )

    def contains(self, point: Vec3D) -> bool:
        return (
            self.min_corner.x <= point.x <= self.max_corner.x
            and self.min_corner.y <= point.y <= self.max_corner.y
            and self.min_corner.z <= point.z <= self.max_corner.z
        )

    def intersects(self, other: "Cuboid") -> bool:
        return (
            self.min_corner.x <= other.max_corner.x
            and self.max_corner.x >= other.min_corner.x
            and self.min_corner.y <= other.max_corner.y
            and self.max_corner.y >= other.min_corner.y
            and self.min_corner.z <= other.max_corner.z
            and self.max_corner.z >= other.min_corner.z
        )


# Example usage
if __name__ == "__main__":
    import logging


def set_boundaries(cuboid, planes, logger):
    errors = []
    for attribute, plane in planes:
        try_set_boundary(cuboid, attribute, plane, errors)

    if errors:
        logger.error("The following boundary errors occurred:")
        for error in errors:
            logger.error(error)
        errors.clear()
    else:
        logger.info("All boundaries set successfully.")


def try_set_boundary(cuboid, attribute, plane, errors):
    try:
        setattr(cuboid, attribute, plane)
    except CuboidBoundaryError as e:
        errors.append(e)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARN)

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Add formatter to console handler
    ch.setFormatter(formatter)

    # Add console handler to logger
    logger.addHandler(ch)

    cuboid = Cuboid(Vec3D(0, 0, 0), Vec3D(10, 10, 10))
    logger.info(f"Width: {cuboid.size.x}")
    logger.info(f"Height: {cuboid.size.y}")
    logger.info(f"Depth: {cuboid.size.z}")
    logger.info(f"Center: {cuboid.center}")

    # Create new Plane objects to set new boundaries
    fov = Vec2D(2, 2)

    plane_min = Plane(Vec3D(4, 4, 2), fov)  # The min corner of the plane_min is now (4, 4, 2)
    plane_max = Plane(Vec3D(16, 16, 2), fov)  # The min corner of the plane_max is now (16, 16, 2)
    plane_z_max = Plane(Vec3D(4, 4, 24), fov)  # The min corner of the plane_z_max is now (4, 4, 24)

    logger.info(f"Plane Min: {plane_min} for setting min_x, min_y, min_z")
    logger.info(f"Plane Max: {plane_max} for setting max_x, max_y")
    logger.info(f"Plane Z Max: {plane_z_max} for setting max_z")

    logger.info(f"\nCurrent Boundaries:")
    logger.info(f"Min Corner: {cuboid.min_corner}")
    logger.info(f"Max Corner: {cuboid.max_corner}")
    logger.info(f"Cuboid Size: {cuboid.size}")

    # List to collect errors
    errors = []

    # Set new boundaries using the Plane objects
    proper_attributes_planes = [
        ("min_x", plane_min),
        ("min_y", plane_min),
        ("min_z", plane_min),
        ("max_x", plane_max),
        ("max_y", plane_max),
        ("max_z", plane_z_max),
    ]
    problematic_attribute_planes = [
        ("max_z", plane_min),
        ("min_z", plane_z_max),
        ("max_x", plane_min),
        ("min_x", plane_max),
        ("max_y", plane_min),
        ("min_y", plane_max),
    ]

    set_boundaries(cuboid, proper_attributes_planes, logger)  # Log all successful boundary settings
    set_boundaries(cuboid, problematic_attribute_planes, logger)

    logger.info(f"\nUpdated Boundaries:")
    logger.info(f"Min Corner: {cuboid.min_corner}")
    logger.info(f"Max Corner: {cuboid.max_corner}")
    logger.info(f"Cuboid Size: {cuboid.size}")

    point = Vec3D(5, 5, 5)
    logger.info(f"Contains point {point}: {cuboid.contains(point)}")

    other_cuboid = Cuboid(Vec3D(5, 5, 5), Vec3D(15, 15, 15))
    logger.info(f"Intersects with other cuboid: {cuboid.intersects(other_cuboid)}")
