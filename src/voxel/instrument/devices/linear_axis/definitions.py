from abc import ABC
from enum import StrEnum


class LinearAxisDimension(StrEnum):
    X = 'X'  # tiling axis
    Y = 'Y'  # tiling axis
    Z = 'Z'  # scanning axis
    N = 'N'  # calibration axis


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
