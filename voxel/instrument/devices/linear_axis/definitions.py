from abc import ABC
from enum import StrEnum


class LinearAxisDimension(StrEnum):
    X = 'tiling_1'
    Y = 'tiling_2'
    Z = 'scanning'
    N = 'calibration'  # for axes not used in defining the stage 3D space e.g. focusing


class ScanType(StrEnum):
    STEP_AND_SHOOT = 'step_and_shoot'
    CONTINUOUS = 'continuous'


class ScanState(StrEnum):
    IDLE = 'idle'
    CONFIGURED = 'configured'
    SCANNING = 'scanning'


class ScanConfig(ABC):
    start_mm: float
    stop_mm: float
    scan_type: ScanType
