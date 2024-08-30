"""
This module provides voxel compatible classes for Coherent lasers.
Coherent: https://www.coherent.com/
"""

from .genesis_mx import GenesisMXLaser
from .obis_ls import ObisLSLaser
from .obis_lx import ObisLXLaser

__all__ = [
    'GenesisMXLaser',
    'ObisLXLaser',
    'ObisLSLaser'
]
