"""
This module provides a class to control voxel compliant Vieworks cameras.
Supported cameras include:
    - Vieworks Camera using eGrabber SDK
"""

from .definitions import VieworksSettings
from .vieworks_egrabber import VieworksCamera

__all__ = [
    'VieworksCamera',
    'VieworksSettings'
]
