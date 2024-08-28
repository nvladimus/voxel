from dataclasses import dataclass

from voxel.descriptors.deliminated_property import deliminated_property
from voxel.devices.controllers.tigerbox import ASITigerBox
from voxel.devices.linear_axis import VoxelLinearAxis, LinearAxisDimension
from voxel.devices.linear_axis.definitions import ScanConfig, ScanState


@dataclass
class ASIStageScanConfig(ScanConfig):
    start_mm: float
    stop_mm: float
    speed_mm_s: float
    acceleration_mm_s2: float


@dataclass
class ASIStepAndShootConfig(ScanConfig):
    start_mm: float
    stop_mm: float
    step_size_um: float
    dwell_time_s: float
    retrace_speed_mm_s: float


@dataclass
class ASITriggeredStepAndShootConfig(ScanConfig):
    start_mm: float
    stop_mm: float
    step_size_um: float


class ASITigerLinearAxis(VoxelLinearAxis):

    def __init__(
            self,
            id: str,
            hardware_axis: str,
            dimension: LinearAxisDimension,
            tigerbox: ASITigerBox,
    ):
        super().__init__(id, dimension)
        self._tigerbox = tigerbox
        self._hardware_axis = hardware_axis.upper()
        try:
            self._tigerbox.register_axis(self.id, self._hardware_axis, self.dimension)
        except ValueError as e:
            raise ValueError(f"Failed to register axis {self.id} with dimension {self.dimension}") from e

    def __repr__(self):
        return (
            f"id:               {self.id}, \n"
            f"hardware_axis:    {self._hardware_axis}, \n"
            f"dimension:        {self.dimension} \n"
            f"position_mm:      {self.position_mm}, \n"
            f"limits_mm:        {self.lower_limit_mm, self.upper_limit_mm}, \n"
            f"speed_mm_s:       {self.speed_mm_s}, \n"
            f"acceleration_ms:  {self.acceleration_ms}, \n"
            f"is_moving:        {self.is_moving}, \n"
        )

    def close(self):
        self._tigerbox.deregister_axis(self.id)

    # Scanning properties and methods ________________________________________________________________________________

    def configure_scan(self, config: ScanConfig):
        if not self.dimension == LinearAxisDimension.Z:
            raise ValueError("Unable to configure scan. This axis is not used for scanning.")
        if isinstance(config, ASITriggeredStepAndShootConfig):
            self._tigerbox.setup_step_shoot_scan(self.id, config.step_size_um)
            return

    def start_scan(self):
        if self.scan_state != ScanState.CONFIGURED:
            raise ValueError("Scan not configured. Call configure_scan first.")
        self._tigerbox.start_scan()

    def stop_scan(self):
        self._tigerbox.stop_scan()

    @property
    def scan_state(self) -> ScanState:
        return self._tigerbox.scan_state

    # Positional properties and methods ______________________________________________________________________________

    @deliminated_property(
        minimum=lambda self: self.lower_limit_mm,
        maximum=lambda self: self.upper_limit_mm,
        unit='mm',
    )
    def position_mm(self) -> float:
        return self._tigerbox.get_axis_position(self.id)

    @position_mm.setter
    def position_mm(self, position_mm: float) -> None:
        self._tigerbox.move_absolute_mm(self.id, position_mm)

    @property
    def upper_limit_mm(self) -> float:
        return self._tigerbox.get_upper_travel_limit(self.id)

    @property
    def lower_limit_mm(self) -> float:
        return self._tigerbox.get_lower_travel_limit(self.id)

    @property
    def is_moving(self) -> bool:
        return self._tigerbox.is_axis_moving(self.id)

    def await_move(self):
        while self.is_moving:
            pass
        self.log.info(f"Axis {self.id} has stopped moving. Current position: {self.position_mm}")

    def set_upper_limit_mm_in_place(self) -> None:
        self._tigerbox.set_upper_travel_limit_in_place(self.id)

    def set_lower_limit_mm_in_place(self) -> None:
        self._tigerbox.set_lower_travel_limit_in_place(self.id)

    def zero_in_place(self) -> None:
        """Set the current position as the zero position"""
        return self._tigerbox.zero_in_place(self.id)

    # Other Kinematic properties and methods __________________________________________________________________________

    @property
    def speed_mm_s(self) -> float | None:
        return self._tigerbox.get_axis_speed(self.id)

    @speed_mm_s.setter
    def speed_mm_s(self, speed_mm_s: float) -> None:
        self._tigerbox.set_axis_speed(self.id, speed_mm_s)

    @property
    def acceleration_ms(self) -> float | None:
        return self._tigerbox.get_axis_acceleration(self.id)

    @acceleration_ms.setter
    def acceleration_ms(self, acceleration_ms: float) -> None:
        self._tigerbox.set_axis_acceleration(self.id, acceleration_ms)

    def set_backlash_mm(self, backlash_mm: float) -> None:
        self._tigerbox.set_axis_backlash(self.id, backlash_mm)

    # Convenience methods ____________________________________________________________________________________________
    def go_to_origin(self, wait=False) -> None:
        """Move the axis to the origin."""
        self.position_mm = 0.0
        if wait:
            self.await_move()

    def zero_at_center(self) -> None:
        """Move the axis to the center of the travel range."""
        self.position_mm = (self.lower_limit_mm + self.upper_limit_mm) / 2
        self.zero_in_place()
        self.await_move()

    def zero_at_upper_limit(self) -> None:
        """Move the axis to the upper limit of the travel range."""
        self.position_mm = self.upper_limit_mm
        self.zero_in_place()
        self.await_move()

    def zero_at_lower_limit(self) -> None:
        """Move the axis to the lower limit of the travel range."""
        self.position_mm = self.lower_limit_mm
        self.zero_in_place()
        self.await_move()
