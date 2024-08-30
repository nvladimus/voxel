from dataclasses import dataclass
from typing import Literal

from tigerasi.device_codes import JoystickInput

from voxel.descriptors.deliminated_property import deliminated_property
from voxel.devices.tigerbox import ASITigerBox
from voxel.devices.linear_axis import VoxelLinearAxis, LinearAxisDimension
from voxel.devices.linear_axis.definitions import ScanConfig, ScanState

ASIJoystickInput = JoystickInput


@dataclass
class ASITriggeredStepAndShootConfig(ScanConfig):
    start_mm: float
    stop_mm: float
    step_size_um: float


class ASITigerLinearAxis(VoxelLinearAxis):
    """ASI Tiger Linear Axis implementation.
    :param id: Unique identifier for the device
    :param hardware_axis: The hardware axis of the stage
    :param dimension: The dimension of the stage
    :param tigerbox: The ASITigerBox instance
    :param joystick_polarity: The polarity of the joystick input
    :param joystick_input: The joystick input to use
    :type id: str
    :type hardware_axis: str
    :type dimension: LinearAxisDimension
    :type tigerbox: ASITigerBox
    :type joystick_polarity: Literal[1, -1]
    :type joystick_input: ASIJoystickInput
    :raises DeviceConnectionError: If the stage with the specified hardware axis is not found or is already registered
    """

    def __init__(
            self,
            id: str,
            hardware_axis: str,
            dimension: LinearAxisDimension,
            tigerbox: ASITigerBox,
            joystick_polarity: Literal[1, -1] = 1,
            joystick_input: ASIJoystickInput = None,
    ):
        super().__init__(id, dimension)
        self._tigerbox = tigerbox
        self._hardware_axis = hardware_axis.upper()
        self._tigerbox.register_linear_axis(
            self.id, self._hardware_axis, self.dimension, joystick_polarity, joystick_input)

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
        self._tigerbox.deregister_device(self.id)

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

    @upper_limit_mm.setter
    def upper_limit_mm(self, upper_limit_mm: float) -> None:
        self._tigerbox.set_upper_travel_limit(self.id, upper_limit_mm)

    def set_upper_limit_mm_in_place(self) -> None:
        self._tigerbox.set_upper_travel_limit_in_place(self.id)

    @property
    def lower_limit_mm(self) -> float:
        return self._tigerbox.get_lower_travel_limit(self.id)

    @lower_limit_mm.setter
    def lower_limit_mm(self, lower_limit_mm: float) -> None:
        self._tigerbox.set_lower_travel_limit(self.id, lower_limit_mm)

    def set_lower_limit_mm_in_place(self) -> None:
        self._tigerbox.set_lower_travel_limit_in_place(self.id)

    @property
    def is_moving(self) -> bool:
        return self._tigerbox.is_axis_moving(self.id)

    def await_movement(self):
        while self.is_moving:
            pass
        self.log.info(f"Axis {self.id} has stopped moving. Current position: {self.position_mm}")

    @property
    def home_position_mm(self) -> float:
        return self._tigerbox.get_axis_home_position(self.id)

    def set_home_position(self, home_position: float = None) -> None:
        """Set the home position of the axis
        :param home_position: The position to set as the home position.
        If None, the current position is set as the home position.
        """
        home_position = home_position or self.position_mm
        self._tigerbox.set_axis_home_position(self.id, home_position)

    def home(self, wait=False) -> None:
        """Move the axis to the home position."""
        self._tigerbox.home(self.id)
        if wait:
            self.await_movement()

    def zero_in_place(self) -> None:
        """Set the current position as the zero position"""
        return self._tigerbox.zero_in_place(self.id)

    def go_to_origin(self, wait=False) -> None:
        """Move the axis to the origin."""
        self.position_mm = 0.0
        if wait:
            self.await_movement()

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

    # Input methods _____________________________________________________________________________________________

    def set_joystick_polarity(self, polarity: Literal[1, -1]) -> None:
        self._tigerbox.set_axis_joystick_polarity(self.id, polarity)

    def enable_joystick(self) -> None:
        self._tigerbox.enable_axis_joystick_input(self.id)

    def disable_joystick(self) -> None:
        self._tigerbox.disable_axis_joystick_input(self.id)

    # Convenience methods ____________________________________________________________________________________________

    def zero_at_center(self) -> None:
        """Move the axis to the center of the travel range."""
        self.position_mm = (self.lower_limit_mm + self.upper_limit_mm) / 2
        self.zero_in_place()
        self.await_movement()

    def zero_at_upper_limit(self) -> None:
        """Move the axis to the upper limit of the travel range."""
        self.position_mm = self.upper_limit_mm
        self.zero_in_place()
        self.await_movement()

    def zero_at_lower_limit(self) -> None:
        """Move the axis to the lower limit of the travel range."""
        self.position_mm = self.lower_limit_mm
        self.zero_in_place()
        self.await_movement()
