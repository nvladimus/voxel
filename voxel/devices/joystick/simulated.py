from voxel.devices.joystick.base import BaseJoystick
import logging

JOYSTICK_AXES = {
    "joystick x": 0,
    "joystick y": 1,
    "wheel z":    2,
    "wheel f":    3,
}

JOYSTICK_POLARITY = {
    "inverted": 0,
    "default": 1,
}

class Joystick(BaseJoystick):

    def __init__(self, joystick_mapping=None):
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self._joystick_mapping = joystick_mapping if joystick_mapping is not None else {"joystick x": 'x',
                                                                                        "joystick y": 'y',
                                                                                        "wheel z":    'z',
                                                                                        "wheel f":    'w'}
        self._stage_axes = ['x', 'y', 'z', 'w', 'm']
        self._joystick_axes = ["joystick x", "joystick y", "wheel z", "wheel f"]

    @property
    def stage_axes(self):
        return self._stage_axes

    @property
    def joystick_mapping(self):
        return self._joystick_mapping

    @joystick_mapping.setter
    def joystick_mapping(self, mapping):
        if list(mapping.keys()) != self.joystick_mapping:
            raise ValueError(f'Mapping keys {mapping.keys()} must match joystick axes {self.joystick_axes}')

        for axis in mapping.values():
            if axis not in self.stage_axes:
                raise ValueError(f'Mapping values {mapping.values()} must match stage axes {self.stage_axes}')

        self._joystick_mapping = mapping

    @property
    def joystick_axes(self):
        return self._joystick_axes