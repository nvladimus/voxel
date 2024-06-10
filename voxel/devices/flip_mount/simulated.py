from . import BaseFlipMount, FlipMountConfig

class SimulatedFlipMount(BaseFlipMount):
    def __init__(self, id, conn, positions, init_pos, init_flip_time_ms):
        super().__init__(id)
        self._conn = conn
        self._positions = positions
        self._init_pos = init_pos
        self._init_flip_time_ms = init_flip_time_ms
        self._inst = None
        self.connect()

    def connect(self):
        self.reset()

    def reset(self):
        self.position = self._init_pos
        self.flip_time_ms = self._init_flip_time_ms

    def disconnect(self):
        self._inst = None

    def wait(self):
        pass

    def toggle(self, wait=False):
        new_pos = 0 if self._inst == 1 else 1
        self._inst = new_pos
        if wait:
            self.wait()

    @property
    def position(self):
        return next((key for key, value in self._positions.items() if value == self._inst), 'Unknown')

    @position.setter
    def position(self, position_name, wait=False):
        self._inst = self._positions[position_name]
        if wait:
            self.wait()

    @property
    def flip_time_ms(self):
        return self._flip_time_ms

    @flip_time_ms.setter
    def flip_time_ms(self, time_ms):
        self._flip_time_ms = time_ms
