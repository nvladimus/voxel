"""
Available downsample processes:
- voxel.processes.downsample.cpu.numpy.downsample_2d
    - NPDownSample2D
- voxel.processes.downsample.cpu.numpy.downsample_3d
    - NPDownSample3D
- voxel.processes.downsample.cpu.tensorstore.downsample_2d
    - TSDownSample2D
- voxel.processes.downsample.cpu.tensorstore.downsample_3d
    - TSDownSample3D
- voxel.processes.downsample.gpu.cucim.downsample_2d
    - CucimDownSample2D
- voxel.processes.downsample.gpu.cucim.downsample_3d
    - CucimDownSample3D
- voxel.processes.downsample.gpu.gputools.downsample_2d
    - GPUToolsDownSample2D
- voxel.processes.downsample.gpu.gputools.downsample_3d
    - GPUToolsDownSample3D
- voxel.processes.downsample.clesperanto.gputools.downsample_2d
    - CLEDownSample2D
- voxel.processes.downsample.clesperanto.gputools.downsample_3d
    - CLEDownSample3D
"""

from .base import BaseDownSample
from voxel.processes.downsample.cpu.numpy.downsample_2d import NPDownSample2D
from voxel.processes.downsample.cpu.numpy.downsample_3d import NPDownSample3D
from voxel.processes.downsample.cpu.tensorstore.downsample_2d import TSDownSample2D
from voxel.processes.downsample.cpu.tensorstore.downsample_3d import TSDownSample3D
from voxel.processes.downsample.gpu.cucim.downsample_2d import CucimDownSample2D
from voxel.processes.downsample.gpu.cucim.downsample_3d import CucimDownSample3D
from voxel.processes.downsample.gpu.gputools.downsample_2d import GPUToolsDownSample2D
from voxel.processes.downsample.gpu.gputools.downsample_3d import GPUToolsDownSample3D
from voxel.processes.downsample.gpu.clesperanto.downsample_2d import CLEDownSample2D
from voxel.processes.downsample.gpu.clesperanto.downsample_3d import CLEDownSample3D

__all__ = [
    "BaseDownSample",
    "NPDownSample2D",
    "NPDownSample3D",
    "TSDownSample2D",
    "TSDownSample3D",
    "CucimDownSample2D",
    "CucimDownSample3D",
    "GPUToolsDownSample2D",
    "GPUToolsDownSample3D",
    "CLEDownSample2D",
    "CLEDownSample3D",
]
