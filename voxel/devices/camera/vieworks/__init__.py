"""
This module provides a class to control voxel compliant Vieworks cameras.
Supported cameras include:
    - Vieworks Camera using eGrabber SDK
"""

from .vieworks_egrabber import VieworksCamera
from .definitions import VieworksSettings

__all__ = [
    'VieworksCamera',
    'VieworksSettings'
]
