"""
Module for a voxel lens device.
"""
from typing import Optional

from voxel.instrument.device import VoxelDevice


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
