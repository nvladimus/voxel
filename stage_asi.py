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
    "On": TTLIn0Mode.REPEAT_LAST_REL_MOVE,
    "Off": TTLIn0Mode.OFF,
}

class StageASI:

    def __init__(self, stage_cfg, tigerbox: TigerController):
        """Connect to hardware.
      
        :param stage_cfg: cfg for stage
        :param tigerbox: TigerController instance.
        """
        self.stage_cfg = stage_cfg
        self.tigerbox = tigerbox
        self.tiger_joystick_mapping = self.tigerbox.get_joystick_axis_mapping()
        self.axes = stage_cfg['instrument_axis']  # list of strings for this Pose's moveable axes in tiger frame.
        self.hardware_axis = stage_cfg['hardware_axis']
        # axis_map: dictionary representing the mapping from sample pose to tigerbox axis.
        # i.e: `axis_map[<sample_frame_axis>] = <tiger_frame_axis>`.
        axis_map = {self.axes: self.hardware_axis}
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        # We assume a bijective axis mapping (one-to-one and onto).
        self.sample_to_tiger_axis_map = {}
        self.tiger_to_sample_axis_map = {}
        self.log.debug("Remapping axes with the convention "
                       "{'sample frame axis': 'machine frame axis'} "
                       f"from the following dict: {axis_map}.")
        self.sample_to_tiger_axis_map = self._sanitize_axis_map(axis_map)
        r_axis_map =  dict(zip(axis_map.values(), axis_map.keys()))
        self.tiger_to_sample_axis_map = self._sanitize_axis_map(r_axis_map)
        self.log.debug(f"New sample to tiger axis mapping: "
                       f"{self.sample_to_tiger_axis_map}")
        self.log.debug(f"New tiger to sample axis mapping: "
                       f"{self.tiger_to_sample_axis_map}")
        print(self.sample_to_tiger_axis_map)
        print(self.tiger_to_sample_axis_map)
        print(self.axes)

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

    def move_relative(self, wait: bool = True, **axes: float):
        axes_moves = "".join([f'{k}={v:.3f} ' for k, v in axes.items()])
        w_text = "" if wait else "NOT "
        self.log.debug(f"Relative move by: {axes_moves}and {w_text}waiting.")
        # Remap to hardware coordinate frame.
        machine_axes = self._sample_to_tiger(axes)
        self.tigerbox.move_relative(**machine_axes, wait=wait)
        if wait:
            while self.is_moving():
                sleep(0.001)

    def move_absolute(self, wait: bool = True, **axes: float):
        """Move the specified axes by their corresponding amounts.

        :param wait: If true, wait for the stage to arrive to the specified
            location. If false, (1) do not wait for the chars to exit the
            serial port, (2) do not wait for stage to respond, and
            (3) do not wait for the stage to arrive at the specified location.
        :param axes: dict, keyed by axis of which axis to move and by how much.
        """
        axes_moves = "".join([f'{k}={v:.3f} ' for k, v in axes.items()])
        w_text = "" if wait else "NOT "
        self.log.debug(f"Absolute move to: {axes_moves}and {w_text}waiting.")
        # Remap to hardware coordinate frame.
        machine_axes = self._sample_to_tiger(axes)
        self.tigerbox.move_absolute(**machine_axes, wait=wait)
        if wait:
            while self.is_moving():
                sleep(0.001)

    @property
    def position(self):
        tiger_position = self.tigerbox.get_position(*self.axes)
        return self._tiger_to_sample(tiger_position)

    @property
    def travel_limits(self):
        """ Get the travel limits for the specified axes.

        :return: a dict of 2-value lists, where the first element is the lower
            travel limit and the second element is the upper travel limit.
        """
        limits = {}
        for ax in self.axes:
            print(ax)
            # Get lower/upper limit in tigerbox frame.
            tiger_ax = self._sample_to_tiger_axis_list(ax)[0]
            tiger_limit_a = self.tigerbox.get_lower_travel_limit(tiger_ax)
            tiger_limit_b = self.tigerbox.get_upper_travel_limit(tiger_ax)
            # Convert to sample frame before returning.
            sample_limit_a = list(self._tiger_to_sample(tiger_limit_a).values())[0]
            sample_limit_b = list(self._tiger_to_sample(tiger_limit_b).values())[0]
            limits[ax] = sorted([sample_limit_a, sample_limit_b])
        return limits

    @property
    def axis_backlash(self):
        """Get the axis backlash compensation."""
        tiger_backlash = self.tigerbox.get_axis_backlash(*self.axes)
        return self._tiger_to_sample(tiger_backlash)

    @axis_backlash.setter
    def axis_backlash(self, **axes: float):
        """Set the axis backlash compensation to a set value (0 to disable)."""
        machine_axes = self._sample_to_tiger(axes)
        for ax in machine_axes:
            self.stage_cfg['backlash_mm'] = machine_axes[ax]
        self.tigerbox.set_axis_backlash(**machine_axes)

    @property
    def speed(self):
        """Get the tiger axis speed."""
        tiger_speed = self.tigerbox.get_speed(*self.axes)
        return self._tiger_to_sample(tiger_speed)

    @speed.setter
    def speed(self, **axes: float):
        """Set the tiger axis speed."""
        machine_axes = self._sample_to_tiger(axes)
        for ax in machine_axes:
            self.stage_cfg['speed_mm_s'] = machine_axes[ax]
        self.tigerbox.set_speed(**machine_axes)

    @property
    def acceleration(self):
        """Get the tiger axis acceleration."""
        tiger_speed = self.tigerbox.get_acceleration(*self.axes)
        return self._tiger_to_sample(tiger_speed)

    @acceleration.setter
    def acceleration(self, **axes: float):
        """Set the tiger axis acceleration."""
        machine_axes = self._sample_to_tiger(axes)
        for ax in machine_axes:
            self.stage_cfg['acceleration_ms'] = machine_axes[ax]
        self.tigerbox.set_acceleration(**machine_axes)

    @property
    def ttl(self):
        """Get the tiger axis ttl."""
        tiger_ttl = self.tigerbox.get_joystick_axis_mapping(*self.axes)
        sample_axes = self._tiger_to_sample(tiger_joystick)
        converted_axes = sample_axes
        for ax in sample_axes:
            ttl_mode = sample_axes[ax]
            converted_axes[ax] = next(key for key, value in TTL_MODES.items() if value == sample_axes[ax])
        return converted_axes

    @ttl.setter
    def ttl(self, **axes: int):
        """Set the tiger axis ttl."""

        valid = list(TTL_MODES.keys())
        for ax in axes:
            if axes[ax] not in valid:
                raise ValueError("ttl must be one of %r." % valid)

        machine_axes = self._sample_to_tiger(axes)
        for ax in machine_axes:
            self.stage_cfg['ttl_mode'] = machine_axes[ax]
            # Grab the card address for this axis
            card_address = tigerbox.axis_to_card[ax]
            self.tigerbox.set_ttl_pin_modes(in0_mode = TTL_MODES[machine_axes[ax]], card_address = card_address)
                
    @property
    def joystick_mapping(self):
        """Get the tiger joystick axis."""
        tiger_joystick = self.tigerbox.get_joystick_axis_mapping(*self.axes)
        sample_axes = self._tiger_to_sample(tiger_joystick)
        converted_axes = sample_axes
        # convert joystick axes from tiger enums to abstracted strings
        for ax in sample_axes:
            joystick_value = samples_axes[ax]
            converted_axes[ax] = next(key for key, value in JOYSTICK_MAPPING.items() if value == sample_axes[ax])
        return converted_axes

    @joystick_mapping.setter
    def joystick_mapping(self, **axes: str):
        """Set the tiger joystick axis."""
        valid = list(JOYSTICK_MAPPING.keys())
        for ax in axes:
            if axes[ax] not in valid:
                raise ValueError("joystick mapping must be one of %r." % valid)

        machine_axes = self._sample_to_tiger(axes)
        for ax in machine_axes:
            self.stage_cfg['joystick_mapping'] = machine_axes[ax]
            self.tigerbox.bind_axis_to_joystick_input({ax: JOYSTICK_MAPPING[machine_axes[ax]]})

    @property
    def joystick_polarity(self):
        """Get the tiger joystick axis polarity."""
        # TODO: not yet implemented in TigerASI
        pass

    @joystick_polarity.setter
    def joystick_polarity(self, **axes: str):
        """Set the tiger joystick axis polarity."""
        valid = list(JOYSTICK_POLARITY.keys())
        for ax in axes:
            if axes[ax] not in valid:
                raise ValueError("joystick polarity must be one of %r." % valid)

        machine_axes = self._sample_to_tiger(axes)
        for ax in machine_axes:
            self.stage_cfg['joystick_polarity'] = machine_axes[ax]
            self.tigerbox.set_joystick_axis_polarity({ax: JOYSTICK_POLARITY[machine_axes[ax]]})

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

    def zero_in_place(self, *axes):
        """set the specified axes to zero or all as zero if none specified."""
        # We must populate the axes explicitly since the tigerbox is shared
        # between camera stage and sample stage.
        if len(axes) == 0:
            axes = self.axes
        return self.tigerbox.zero_in_place(*axes)

    def log_metadata(self):
        self.log.info('tiger motorized axes parameters')
        build_config = self.tigerbox.get_build_config()
        self.log.debug(f'{build_config}')
        axis_settings = self.tigerbox.get_info(self.axes)
        for setting in axis_settings:
            self.log.info(f'{axis} axis, {setting}, {axis_settings[setting]}')