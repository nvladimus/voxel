"""
This module provides a class to control voxel compliant Vieworks cameras.
Supported cameras include:
    - Vieworks Camera using eGrabber SDK
"""

from .vieworks_egrabber import VieworksCamera

__all__ = ['VieworksCamera']
