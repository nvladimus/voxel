from .base import VoxelTunableLens, TunableLensControlMode


class SimulatedTunableLens(VoxelTunableLens):
    def __init__(self, id: str):
        super().__init__(id)

    @property
    def mode(self) -> TunableLensControlMode:
        return TunableLensControlMode.INTERNAL

    @mode.setter
    def mode(self, mode: TunableLensControlMode):
        pass

    @property
    def temperature_c(self) -> float:
        return 25.0

    def log_metadata(self):
        return {
            "id": self.id,
            "mode": self.mode,
            "temperature_c": self.temperature_c,
        }

    def close(self):
        pass
