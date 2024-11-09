import logging

from tigerasi.device_codes import *
from tigerasi.tiger_controller import TigerController

from voxel.devices.joystick.base import BaseJoystick

LEFT_WHEELS = list()
RIGHT_WHEELS = list()
Y_JOYSTICKS = list()
X_JOYSTICKS = list()


class Joystick(BaseJoystick):

    def __init__(self, tigerbox: TigerController, axis_mapping: dict):
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)

        self.tigerbox = tigerbox
        self.axis_mapping = axis_mapping
        for key, value in self.axis_mapping.items():
            LEFT_WHEELS.append(key)
            RIGHT_WHEELS.append(key)
            Y_JOYSTICKS.append(key)
            X_JOYSTICKS.append(key)
        self._stage_axes = {
            v: k for k, v in self.axis_mapping.items() if k.upper() in self.tigerbox.axes and v.upper() in self.tigerbox.axes
        }
        for axis in self.tigerbox.axes:
            if axis.lower() not in self._stage_axes.keys():
                self._stage_axes[axis.lower()] = axis.lower()
                self.axis_mapping[axis.lower()] = axis.lower()

        # get initial joystick values
        self._left_wheel = self.tigerbox.get_joystick_axis_mapping(JoystickInput.F_WHEEL)
        self._right_wheel = self.tigerbox.get_joystick_axis_mapping(JoystickInput.Z_WHEEL)
        self._y_joystick = self.tigerbox.get_joystick_axis_mapping(JoystickInput.JOYSTICK_Y)
        self._x_joystick = self.tigerbox.get_joystick_axis_mapping(JoystickInput.JOYSTICK_X)

    @property
    def left_wheel(self):
        return self._left_wheel

    @left_wheel.setter
    def left_wheel(self, axis):
        if axis not in LEFT_WHEELS:
            raise ValueError(f"axis {axis} is not a valid axis for this instrument")
        self.tigerbox.bind_axis_to_joystick_input(self._stage_axes[axis], JoystickInput.F_WHEEL)

    # @property
    # def left_wheel_polarity(self):
    #     return self._left_wheel_polarity

    # @left_wheel_polarity.setter
    # def left_wheel_polarity(self, polarity):
    #     if polarity not in POLARITIES:
    #         raise ValueError(f"polarity {polarity} is not a valid polarity for this axis")
    #     axis = self.tigerbox.get_joystick_axis_mapping(JoystickInput.F_WHEEL)
    #     self.tigerbox.set_joystick_axis_polarity(axis, POLARITIES[polarity])

    @property
    def right_wheel(self):
        return self._right_wheel

    @right_wheel.setter
    def right_wheel(self, axis):
        if axis not in RIGHT_WHEELS:
            raise ValueError(f"axis {axis} is not a valid axis for this instrument")
        self.tigerbox.bind_axis_to_joystick_input(self._stage_axes[axis], JoystickInput.Z_WHEEL)

    # @property
    # def right_wheel_polarity(self):
    #     return self._right_wheel_polarity

    # @right_wheel_polarity.setter
    # def right_wheel_polarity(self, polarity):
    #     if polarity not in POLARITIES:
    #         raise ValueError(f"polarity {polarity} is not a valid polarity for this axis")
    #     axis = self.tigerbox.get_joystick_axis_mapping(JoystickInput.Z_WHEEL)
    #     self.tigerbox.set_joystick_axis_polarity(axis, POLARITIES[polarity])

    @property
    def y_joystick(self):
        return self._y_joystick

    @y_joystick.setter
    def y_joystick(self, axis):
        if axis not in Y_JOYSTICKS:
            raise ValueError(f"axis {axis} is not a valid axis for this instrument")
        self.tigerbox.bind_axis_to_joystick_input(self._stage_axes[axis], JoystickInput.JOYSTICK_Y)

    # @property
    # def y_joystick_polarity(self):
    #     return self._y_joystick_polarity

    # @y_joystick_polarity.setter
    # def y_joystick_polarity(self, polarity):
    #     if polarity not in POLARITIES:
    #         raise ValueError(f"polarity {polarity} is not a valid polarity for this axis")
    #     axis = self.tigerbox.get_joystick_axis_mapping(JoystickInput.JOYSTICK_Y)
    #     self.tigerbox.set_joystick_axis_polarity(axis, POLARITIES[polarity])

    @property
    def x_joystick(self):
        return self._x_joystick

    @x_joystick.setter
    def x_joystick(self, axis):
        if axis not in X_JOYSTICKS:
            raise ValueError(f"axis {axis} is not a valid axis for this instrument")
        self.tigerbox.bind_axis_to_joystick_input(self._stage_axes[axis], JoystickInput.JOYSTICK_X)

    # @property
    # def x_joystick_polarity(self):
    #     return self._x_joystick_polarity

    # @x_joystick_polarity.setter
    # def x_joystick_polarity(self, polarity):
    #     if polarity not in POLARITIES:
    #         raise ValueError(f"polarity {polarity} is not a valid polarity for this axis")
    #     axis = self.tigerbox.get_joystick_axis_mapping(JoystickInput.JOYSTICK_X)
    #     self.tigerbox.set_joystick_axis_polarity(axis, POLARITIES[polarity])

