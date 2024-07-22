"""
This module contains support for cameras that are compliant with Voxel.
BaseCamera describes the interface that all Voxel compliant cameras must implement.
Supported cameras include:
    - Vieworks Camera using eGrabber SDK
    - Hamamatsu Camera using DCAM SDK
    - PCO Camera using PCO SDK
Import the specific camera class from the appropriate sub-module.
e.g. from voxel.devices.camera.vieworks import VieworksCamera
"""

from .base import BaseCamera

__all__ = [
    'BaseCamera',
]