import logging
from pylablib.devices import Thorlabs

MIN_SWITCH_TIME_S = 0.3
MAX_SWITCH_TIME_S = 2.8
VALID_POSITIONS = [0, 1]


class FlipMount:
    def __init__(self, id: str, positions: dict):
        self.log = logging.getLogger(__name__ + "." + self.__class__.__name__)
        self.id = id  # serial number of flip mount
        self.positions = positions   # dict of names and their positions
        # check that all positions are valid
        if not all([pos in VALID_POSITIONS
                    for _,pos in self.positions.items()]):
            raise ValueError(f'positions must be {VALID_POSITIONS}')
        # lets find the device using pyvisa
        devices = Thorlabs.list_kinesis_devices()
        # device = [(serial number, name)]
        try:
            for device in devices:
                # uses the MFF class within
                # devices/Thorlabs/kinesis of pylablib
                flip_mount = Thorlabs.MFF(conn=device[0])
                info = flip_mount.get_device_info()
                if info['serial'] == id:
                    self.flip_mount = flip_mount
                    break
        except:
            self.log.debug(f'{id} is not a valid thorabs flip mount')
            raise ValueError(f'could not find power meter with id {id}')

    @property
    def position(self):
        # returns 0 or 1 for position of flip mount
        position = self.flip_mount.get_state()
        return next(key for key, value in
                    self.filters.items() if value == position)

    @position.setter
    def position(self, position_name: str):
        # returns 0 or 1 for position of flip mount
        if position_name not in self.positions.keys():
            raise ValueError(f'position {position_name}'
                             f'not in {self.positions.keys()}')
        self.flip_mount.move_to_state(self.positions[position_name])
        self.log.info(f'flip mount {self.id}'
                      f'moved to position {position_name}')
    
    @property
    def switch_time_ms(self):
        # returns the time it takes to switch between states
        parameters = self.flip_mount.get_flipper_parameters()
        # returns TFlipperParameters(
        # transit_time*1E-3, # converted from ms to s
        # io1_oper_mode,
        # io1_sig_mode,
        # io1_pulse_width*1E-3,
        # io2_oper_mode,
        # io2_sig_mode,
        # io2_pulse_width*1E-3)
        # we only care about the transit time, return in ms
        return parameters.transit_time*1000
    
    @switch_time_ms.setter
    def switch_time_ms(self, time_ms: float):
        # set the time it takes to switch between states
        if time_ms < MIN_SWITCH_TIME_S * 1000 or \
           time_ms > MAX_SWITCH_TIME_S * 1000:
            raise ValueError(f'switch time {time_ms} must be <'
                             f'{MAX_SWITCH_TIME_S} and > {MIN_SWITCH_TIME_S}')
        self.flip_mount.setup_flipper(transit_time=time_ms/1000)
        self.log.info(f'flip mount {self.id} switch time set to {time_ms} ms')

    def close(self):
        # inherited close property from kinesis in pylablib
        self.close()
        self.log.info(f'power meter {self.id} closed')
