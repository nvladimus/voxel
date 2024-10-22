"""
This module provides voxel compatible classes for Coherent lasers.
Coherent: https://www.coherent.com/

Other drivers for Coherent lasers are available in the following repositories:
- Coherent-lasers: https://github.com/AllenNeuralDynamics/coherent-lasers
"""

from .obis_ls import ObisLSLaser
from .obis_lx import ObisLXLaser

__all__ = ["ObisLXLaser", "ObisLSLaser"]
