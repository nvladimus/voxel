import time
from pylablib.devices import Thorlabs
from typing import Literal, Optional
from voxel.devices.flip_mount.base import BaseFlipMount

VALID_POSITIONS = [0, 1]

class ThorlabsMFF101(BaseFlipMount):
    def __init__(self, id: str, address: str, positions: dict[str, Literal[0, 1]]):
        super().__init__(id)
        self.address = address
        self.positions = positions if self.validate_positions(positions) else {}
        self.inst: Optional[Thorlabs.MFF] = None

    @staticmethod
    def validate_positions(positions: dict) -> bool:
        if not all([pos in VALID_POSITIONS for pos in positions.values()]):
            raise ValueError(f'Positions must be {VALID_POSITIONS}')
        return True

    def connect(self):
        try:
            self.inst = Thorlabs.MFF(conn=self.address)
            self.inst.move_to_state(list(self.positions.values())[0])
            self.inst.setup_flipper(transit_time=1)
        except Exception as e:
            self.log.error(f'Could not connect to flip mount {self.id}: {e}')
            raise e

    def disconnect(self):
        if self.inst is not None:
            self.inst.close()
            self.inst = None
            self.log.info(f'Flip mount {self.id} disconnected')

    @property
    def position(self) -> str:
        if self.inst is None: raise ValueError('Flip mount not connected')
        pos_idx =  self.inst.get_state()
        return next(key for key, value in self.positions.items() if value == pos_idx)

    @position.setter
    def position(self, position_name: str, wait: bool = True):
        if self.inst is None: raise ValueError('Flip mount not connected')
        if position_name not in self.positions:
            raise ValueError(f'Invalid position {position_name}. Valid positions are {list(self.positions.keys())}')
        self.inst.move_to_state(self.positions[position_name])
        self.log.info(f'Flip mount {self.id} moved to position {position_name}')
        if wait:
            time.sleep(self.switch_time_ms * 1e-3)

    def toggle(self, wait: bool = True):
        if self.inst is None: raise ValueError('Flip mount not connected')
        new_pos = 0 if self.inst.get_state() == 1 else 1
        self.inst.move_to_state(new_pos)
        if wait:
            time.sleep(self.switch_time_ms * 1e-3)

    @property
    def switch_time_ms(self) -> float:
        if self.inst is None:
            raise ValueError('Flip mount not connected')
        parameters = self.inst.get_flipper_parameters()
        return parameters.transit_time * 1e3

    @switch_time_ms.setter
    def switch_time_ms(self, time_ms: float):
        if self.inst is None: raise ValueError('Flip mount not connected')
        if not isinstance(time_ms, (int, float)) or time_ms <= 0:
            raise ValueError('Switch time must be a positive number')
        self.inst.setup_flipper(transit_time=time_ms/1000)
        self.log.info(f'Flip mount {self.id} switch time set to {time_ms} ms')