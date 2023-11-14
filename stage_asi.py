import logging
from tigerasi.tiger_controller import TigerController, STEPS_PER_UM
from tigerasi.device_codes import TTLIn0Mode, JoystickInput, JoystickPolarity

# constants for Tiger ASI hardware

JOYSTICK_MAPPING = {
    "joystick x": JoystickInput.JOYSTICK_Y,
    "joystick y": JoystickInput.JOYSTICK_X,
    "wheel z":    JoystickInput.Z_WHEEL,
    "wheel f":    JoystickInput.F_WHEEL,
}

JOYSTICK_POLARITY = {
    "inverted": JoystickPolarity.INVERTED,
    "default": JoystickPolarity.DEFAULT,
}

TTL_MODES = {
    "on": TTLIn0Mode.REPEAT_LAST_REL_MOVE,
    "off": TTLIn0Mode.OFF,
}

class StageASI:

    def __init__(self, tigerbox: TigerController, hardware_axis: str, instrument_axis: str):
        """Connect to hardware.

        :param tigerbox: TigerController instance.
        :param hardware_axis: stage hardware axis.
        :param instrument_axis: instrument hardware axis.
        """
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.tigerbox = tigerbox
        self.hardware_axis = hardware_axis
        self.instrument_axis = instrument_axis
        # axis_map: dictionary representing the mapping from sample pose to tigerbox axis.
        # i.e: `axis_map[<sample_frame_axis>] = <tiger_frame_axis>`.
        axis_map = {self.instrument_axis: self.hardware_axis}
        # We assume a bijective axis mapping (one-to-one and onto).
        self.instrument_to_hardware_axis_map = {}
        self.hardware_to_instrument_axis_map = {}
        self.log.debug("Remapping axes with the convention "
                       "{'instrument axis': 'hardware axis'} "
                       f"from the following dict: {axis_map}.")
        self.instrument_to_hardware_axis_map = self._sanitize_axis_map(axis_map)
        r_axis_map =  dict(zip(axis_map.values(), axis_map.keys()))
        self.hardware_to_instrument_axis_map = self._sanitize_axis_map(r_axis_map)
        self.log.debug(f"New instrument to hardware axis mapping: "
                       f"{self.instrument_to_hardware_axis_map}")
        self.log.debug(f"New hardware to instrument axis mapping: "
                       f"{self.hardware_to_instrument_axis_map}")
        self.tiger_joystick_mapping = self.tigerbox.get_joystick_axis_mapping()
        print(self.instrument_to_hardware_axis_map)
        print(self.hardware_to_instrument_axis_map)

    def _sanitize_axis_map(self, axis_map: dict):
        """save an input axis mapping to apply to move commands.

        :param axis_map: dict, where the key (str) is the desired coordinate
            axis and the value (str) is the underlying machine coordinate axis.
            Note that the value may be signed, i.e: '-y'.
        """
        # Move negative signs off keys and onto values.
        sanitized_axis_map = {}
        for axis, t_axis in axis_map.items():
            axis = axis.lower()
            t_axis = t_axis.lower()
            sign = "-" if axis.startswith("-") ^ t_axis.startswith("-") else ""
            sanitized_axis_map[axis.lstrip("-")] = f"{sign}{t_axis.lstrip('-')}"
        return sanitized_axis_map

    def _remap(self, axes: dict, mapping: dict):
        """remap input axes to their corresponding output axes.

        Input axes is the desired coordinate frame convention;
        output axes are the axes as interpreted by the underlying hardware.

        :returns: either: a list of axes remapped to the new names
            or a dict of moves with the keys remapped to the underlying
            underlying hardware axes and the values unchanged.
        """
        new_axes = {}
        for axis, value in axes.items():
            axis = axis.lower()
            # Default to same axis if no remapped axis exists.
            new_axis = mapping.get(axis, axis)  # Get new key.
            negative = 1 if new_axis.startswith('-') else 0
            new_axes[new_axis.lstrip('-')] = (-1)**negative * value # Get new value.
        return new_axes

    def _sample_to_tiger(self, axes: dict):
        """Remap a position or position delta specified in the sample frame to
        the tiger frame.

        :return: a dict of the position or position delta specified in the
            tiger frame
        """
        return self._remap(axes, self.sample_to_tiger_axis_map)

    def _sample_to_tiger_axis_list(self, *axes):
        """Return the axis specified in the sample frame to axis in the tiger
        frame. Minus signs are omitted."""
        # Easiest way to convert is to temporarily convert into dict.
        axes_dict = {x: 0 for x in axes}
        tiger_axes_dict = self._sample_to_tiger(axes_dict)
        return list(tiger_axes_dict.keys())

    def _tiger_to_sample(self, axes: dict):
        """Remap a position or position delta specified in the tiger frame to
        the sample frame.

        :return: a dict of the position or position delta specified in the
            sample frame
        """
        return self._remap(axes, self.tiger_to_sample_axis_map)

    def move_relative(self, wait: bool = True, position: float):
        w_text = "" if wait else "NOT "
        self.log.debug(f"Relative move by: {axes_moves}and {w_text}waiting.")
        self.tigerbox.move_relative(**{self.hardware_axis: position}, wait=wait)
        if wait:
            while self.is_moving():
                sleep(0.001)

    def move_absolute(self, wait: bool = True, position: float):
        """Move the specified axes by their corresponding amounts.

        :param wait: If true, wait for the stage to arrive to the specified
            location. If false, (1) do not wait for the chars to exit the
            serial port, (2) do not wait for stage to respond, and
            (3) do not wait for the stage to arrive at the specified location.
        :param position: float, keyed by axis of which axis to move and by how much.
        """
        w_text = "" if wait else "NOT "
        self.log.debug(f"Absolute move to: {axes_moves}and {w_text}waiting.")
        self.tigerbox.move_absolute(**{self.hardware_axis: position}, wait=wait)
        if wait:
            while self.is_moving():
                sleep(0.001)

    @property
    def position(self):
        tiger_position = self.tigerbox.get_position(self.hardware_axis)
        return self._tiger_to_sample(tiger_position)

    @property
    def travel_limits(self):
        """ Get the travel limits for the specified axes.

        :return: a dict of 2-value lists, where the first element is the lower
            travel limit and the second element is the upper travel limit.
        """
        limits = {}
        # Get lower/upper limit in tigerbox frame.
        tiger_limit_lower = self.tigerbox.get_lower_travel_limit(self.hardware_axis)
        tiger_limit_upper = self.tigerbox.get_upper_travel_limit(self.hardware_axis)
        # Convert to sample frame before returning.
        sample_limit_lower = list(self._tiger_to_sample(tiger_limit_lower).values())[0]
        sample_limit_upper = list(self._tiger_to_sample(tiger_limit_upper).values())[0]
        limits[self.instrument_axis] = sorted([sample_limit_a, sample_limit_b])
        return limits

    @property
    def axis_backlash(self):
        """Get the axis backlash compensation."""
        tiger_backlash = self.tigerbox.get_axis_backlash(self.hardware_axis)
        return self._tiger_to_sample(tiger_backlash)

    @axis_backlash.setter
    def axis_backlash(self, backlash: float):
        """Set the axis backlash compensation to a set value (0 to disable)."""
        self.tigerbox.set_axis_backlash(**{self.hardware_axis: round(backlash, MM_SCALE)})

    @property
    def speed(self):
        """Get the tiger axis speed."""
        tiger_speed = self.tigerbox.get_speed(self.hardware_axis)
        return self._tiger_to_sample(tiger_speed)

    @speed.setter
    def speed(self, speed: float):
        self.tigerbox.set_speed(**{self.hardware_axis: round(speed, MM_SCALE)})

    @property
    def acceleration(self):
        """Get the tiger axis acceleration."""
        tiger_speed = self.tigerbox.get_acceleration(self.hardware_axis)
        return self._tiger_to_sample(tiger_speed)

    @acceleration.setter
    def acceleration(self, acceleration: float):
        """Set the tiger axis acceleration."""
        self.tigerbox.set_acceleration(**{self.hardware_axis: round(speed, MS_SCALE)})

    @property
    def ttl(self):
        """Get the tiger axis ttl."""
        card_address = self.tigerbox.axis_to_card[self.hardware_axis][0]
        print(card_address)
        tiger_ttl = self.tigerbox.get_ttl_output_state()
        print(tiger_ttl)
        sample_axes = self._tiger_to_sample(tiger_ttl)
        print(sample_axis)
        # converted_axes = sample_axes
        # for ax in sample_axes:
        #     ttl_mode = sample_axes[ax]
        #     converted_axes[ax] = next(key for key, value in TTL_MODES.items() if value == sample_axes[ax])
        # return converted_axes

    @ttl.setter
    def ttl(self, mode: int):
        """Set the tiger axis ttl."""

        valid = list(TTL_MODES.keys())
        if mode not in valid:
            raise ValueError("ttl must be one of %r." % valid)

        card_address = tigerbox.axis_to_card[self.hardware_axis]
        self.tigerbox.set_ttl_pin_modes(in0_mode = TTL_MODES[mode], card_address = card_address)
                
    @property
    def joystick_mapping(self):
        """Get the tiger joystick axis."""
        tiger_joystick = self.tigerbox.get_joystick_axis_mapping(self.hardware_axis)
        sample_axes = self._tiger_to_sample(tiger_joystick)
        converted_axes = sample_axes
        # convert joystick axes from tiger enums to abstracted strings
        joystick_value = samples_axes
        converted_axes = next(key for key, value in JOYSTICK_MAPPING.items() if value == sample_axes)
        return converted_axes

    @joystick_mapping.setter
    def joystick_mapping(self, mapping: str):
        """Set the tiger joystick axis."""
        valid = list(JOYSTICK_MAPPING.keys())
        if mapping not in valid:
            raise ValueError("joystick mapping must be one of %r." % valid)

        self.tigerbox.bind_axis_to_joystick_input({self.hardware_axis: JOYSTICK_MAPPING[mapping]})

    @property
    def joystick_polarity(self):
        """Get the tiger joystick axis polarity."""
        # TODO: not yet implemented in TigerASI
        pass

    @joystick_polarity.setter
    def joystick_polarity(self, polarity: str):
        """Set the tiger joystick axis polarity."""
        valid = list(JOYSTICK_POLARITY.keys())
        if polarity not in valid:
            raise ValueError("joystick polarity must be one of %r." % valid)

        self.tigerbox.set_joystick_axis_polarity({self.hardware_axis: JOYSTICK_POLARITY[polarity]})

    def lock_external_user_input(self):
        self.log.info("Locking joystick control.")
        # Save current joystick axis map, since enabling it will restore
        # a "default" axis map, which isn't necessarily what we want.
        self.tiger_joystick_mapping = self.tigerbox.get_joystick_axis_mapping()
        self.tigerbox.disable_joystick_inputs()

    def unlock_external_user_input(self):
        self.log.info("Releasing joystick control.")
        self.tigerbox.enable_joystick_inputs()
        # Re-apply our joystick axis map to restore joystick state correctly.
        self.tigerbox.bind_axis_to_joystick_input(**self.tiger_joystick_mapping)

    def is_moving(self):
        return self.tigerbox.is_moving()

    def axis_is_moving(self):
        # TODO: merge and check TigerASI PR on this function
        return self.tigerbox.axis_is_moving()

    def zero_in_place(self):
        """set the specified axes to zero or all as zero if none specified."""
        # We must populate the axes explicitly since the tigerbox is shared
        # between camera stage and sample stage.
        return self.tigerbox.zero_in_place(self.hardware_axis)

    def log_metadata(self):
        self.log.info('tiger motorized axes parameters')
        build_config = self.tigerbox.get_build_config()
        self.log.debug(f'{build_config}')
        axis_settings = self.tigerbox.get_info(self.axes)
        for setting in axis_settings:
            self.log.info(f'{axis} axis, {setting}, {axis_settings[setting]}')