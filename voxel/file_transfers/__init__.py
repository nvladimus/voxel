"""
Available file transfer processes:
- voxel.file_transfers.robocopy
    - RobocopyFileTransfer
- voxel.file_transfers.rsync
    - RsyncFileTransfer
"""

from .base import BaseFileTransfer
from voxel.file_transfers.robocopy import RobocopyFileTransfer
from voxel.file_transfers.rsync import RsyncFileTransfer

__all__ = [
    "BaseFileTransfer",
    "RobocopyFileTransfer",
    "RsyncFileTransfer"
]
