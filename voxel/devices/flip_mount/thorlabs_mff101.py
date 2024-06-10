import time
from typing import Optional

from pylablib.devices import Thorlabs

from voxel.descriptors.deliminated_property import DeliminatedProperty
from . import BaseFlipMount, FlipMountConfig

VALID_POSITIONS = [0, 1]
FLIP_TIME_RANGE = (500, 2800)


class ThorlabsMFF101(BaseFlipMount):
    def __init__(self, config: FlipMountConfig):
        super().__init__(config.id)
        self._conn = config.conn
        self._positions = config.positions
        self._inst: Optional[Thorlabs.MFF] = None
        self._init_pos = config.init_pos
        self._init_flip_time_ms = config.init_flip_time_ms
        self.connect()

    def connect(self):
        try:
            self._inst = Thorlabs.MFF(conn=self._conn)
            self.reset()
        except Exception as e:
            self.log.error(f'Could not connect to flip mount {self.id}: {e}')
            raise e

    def reset(self):
        if self._inst is None: raise ValueError(f'Unable to reset {self.id} Flip mount not connected')
        self.position = self._init_pos
        self.flip_time_ms = self._init_flip_time_ms

    def disconnect(self):
        if self._inst is not None:
            self._inst.close()
            self._inst = None
            self.log.info(f'Flip mount {self.id} disconnected')

    def wait(self):
        time.sleep(self.flip_time_ms * 1e-3) # type: ignore

    def toggle(self, wait=False):
        if self._inst is None: raise ValueError('Flip mount not connected')
        new_pos = 0 if self._inst.get_state() == 1 else 1
        self._inst.move_to_state(new_pos)
        if wait:
            self.wait()

    @property
    def position(self) -> str | None:
        if self._inst is None: raise ValueError(f'Position not found for {self.id} Flip mount not connected')
        pos_idx =  self._inst.get_state()
        return next((key for key, value in self._positions.items() if value == pos_idx), 'Unknown')

    @position.setter
    def position(self, position_name: str):
        if self._inst is None:
            raise ValueError('Flip mount not connected')
        if position_name not in self._positions:
            raise ValueError(f'Invalid position {position_name}. Valid positions are {list(self._positions.keys())}')
        self._inst.move_to_state(self._positions[position_name])
        self.log.info(f'Flip mount {self.id} moved to position {position_name}')

    @DeliminatedProperty(minimum=FLIP_TIME_RANGE[0], maximum=FLIP_TIME_RANGE[1], step=100)
    def flip_time_ms(self) -> int:
        if self._inst is None:
            raise ValueError('Flip mount not connected')
        try:
            parameters = self._inst.get_flipper_parameters()
            flip_time_ms: int = int((parameters.transit_time) * 1e3)
        except Exception:
            # flip_time_ms = float((FLIP_TIME_RANGE[0] + FLIP_TIME_RANGE[1]) / 2) # sets to mid value
            raise ValueError('Could not get flip time')
        return flip_time_ms

    @flip_time_ms.setter
    def flip_time_ms(self, time_ms: float):
        if self._inst is None: raise ValueError('Flip mount not connected')
        if not isinstance(time_ms, (int, float)) or time_ms <= 0:
            raise ValueError('Switch time must be a positive number')
        clamped_time_ms = int(max(FLIP_TIME_RANGE[0], min(time_ms, FLIP_TIME_RANGE[1])))
        try:
            self._inst.setup_flipper(transit_time=clamped_time_ms/1000)
            self.log.info(f'Flip mount {self.id} switch time set to {clamped_time_ms} ms')
        except Exception as e:
            raise ValueError(f'Could not set flip time: {e}')