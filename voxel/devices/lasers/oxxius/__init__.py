"""
This module provides voxel compatible classes for Oxxius lasers.
Oxxius: https://www.oxxius.com/
"""

from .oxxius_lbx import LaserLBXOxxius as OxxiusLBXLaser
from .oxxius_lcx import LaserLCXOxxius as OxxiusLCXLaser

__all__ = [
    'OxxiusLBXLaser',
    'OxxiusLCXLaser'
]
