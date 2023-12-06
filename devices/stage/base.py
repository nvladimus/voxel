import inspect

class BaseStage:

    def move_relative(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def move_absolute(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def setup_stage_scan(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def start_stage_scan(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def position(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def limits(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def backlash(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @backlash.setter
    def backlash(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def speed(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @speed.setter
    def speed(self, speed: float):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def acceleration(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @acceleration.setter
    def acceleration(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def mode(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @mode.setter
    def mode(self, mode: int):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass
                
    @property
    def joystick_mapping(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @joystick_mapping.setter
    def joystick_mapping(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @property
    def joystick_polarity(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    @joystick_polarity.setter
    def joystick_polarity(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def lock_external_user_input(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def unlock_external_user_input(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def is_axis_moving(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def zero_in_place(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass

    def log_metadata(self):
        self.log.warning(f"WARNING: {inspect.stack()[0][3]} not implemented")
        pass