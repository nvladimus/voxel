"""
Module for a voxel lens device.
"""
from dataclasses import dataclass
from typing import Optional

from utils.geometry import Vec2D
from voxel.instrument.device import VoxelDevice



# TODO: Figure out the best way to model a lens device.
class VoxelLens(VoxelDevice):
    """A voxel lens device."""

    def __init__(self,
                 magnification: float,
                 name: Optional[str] = None,
                 focal_length_um: Optional[float] = None,
                 aperture_um: Optional[float] = None,
                 ):
        super().__init__(name)
        self.magnification = magnification
        self.focal_length_um = focal_length_um
        self.aperture_um = aperture_um

    def close(self):
        """Close the lens."""
        pass


@dataclass
class Camera:
    """A camera device."""
    name: str
    sensor_size_px: Vec2D
    sensor_size_um: Vec2D


if __name__ == "__main__":
    lens = VoxelLens(2.0, "Lens1", 50.0, 2.0)
    print(lens)
    camera = Camera("Camera1", Vec2D(4e4, 3e4), Vec2D(5120, 4096))
    print(camera)
    fov = camera.sensor_size_um / lens.magnification
    print(f"Field of view: {fov}")
