import math
from dataclasses import dataclass
from typing import List, Dict, Callable, Optional, Tuple

from ruamel.yaml import YAML

from voxel import VoxelInstrument
from voxel.acquisition.frame_stack import FrameStack
from voxel.acquisition.scan_path import (
    ScanPattern, ScanDirection, StartCorner,
    generate_raster_path, generate_serpentine_path,
    generate_spiral_path, adjust_for_start_corner
)
from voxel.acquisition.volume import Volume
from voxel.instrument.channel import VoxelChannel
from voxel.utils.descriptors.enumerated_property import enumerated_property
from voxel.utils.geometry.vec import Vec2D, Vec3D

DEFAULT_TILE_OVERLAP = 0.15


@dataclass(frozen=True)
class AcquisitionPlan:
    frame_stacks: Dict[Vec2D, FrameStack]
    scan_path: List[Vec2D]

    def __post_init__(self):
        if not self.scan_path:
            raise ValueError("Scan path cannot be empty")
        if not all(idx in self.frame_stacks for idx in self.scan_path):
            raise ValueError("Scan path contains indices not present in frame stacks")

    def __len__(self):
        return len(self.scan_path)

    def __eq__(self, other: 'AcquisitionPlan') -> bool:
        if not isinstance(other, AcquisitionPlan):
            return NotImplemented

        return self.frame_stacks == other.frame_stacks and self.scan_path == other.scan_path

    def __ne__(self, other: 'AcquisitionPlan') -> bool:
        return not self.__eq__(other)

    def to_dict(self):
        return {
            "frame_stacks": {str(idx): frame_stack.to_dict() for idx, frame_stack in self.frame_stacks.items()},
            "scan_path": [str(idx) for idx in self.scan_path]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, Dict[str, any]]]) -> 'AcquisitionPlan':
        frame_stacks = {}
        for idx_str, frame_stack_data in data["frame_stacks"].items():
            idx = Vec2D.from_str(idx_str)
            frame_stacks[idx] = FrameStack.from_dict(frame_stack_data)
        scan_path = [Vec2D.from_str(idx_str) for idx_str in data["scan_path"]]
        return cls(frame_stacks, scan_path)


class AcquisitionPlanner:
    def __init__(
            self,
            instrument: 'VoxelInstrument',
            z_step_size: float,
            channel_names: List[str],
            file_path: str,
            tile_overlap: float = DEFAULT_TILE_OVERLAP,
            scan_pattern: ScanPattern = ScanPattern.RASTER,
            scan_direction: ScanDirection = ScanDirection.ROW_WISE,
            start_corner: StartCorner = StartCorner.TOP_LEFT,
            reverse_scan_path: bool = False,
            volume_limits_mm: Optional[Tuple[Vec3D, Vec3D]] = None
    ) -> None:
        self.instrument = instrument
        self.channels = [instrument.channels[channel_name] for channel_name in channel_names]
        self.file_path = file_path

        self._z_step_size = z_step_size
        self._tile_overlap = tile_overlap
        self._scan_pattern = scan_pattern
        self._scan_direction = scan_direction
        self._start_corner = start_corner
        self._reverse_scan_path = reverse_scan_path

        self._observers: List[Callable[[], None]] = []
        self._hash = None

        if not volume_limits_mm:
            volume_limits_mm = instrument.stage.limits_mm[0], instrument.stage.limits_mm[1]
        self.volume = Volume(volume_limits_mm[0], volume_limits_mm[1], self.z_step_size)
        self.volume.add_observer(self._regenerate_plan)

        self.plan = self._generate_acquisition_plan()

    def add_observer(self, callback: Callable[[], None]):
        self._observers.append(callback)

    def _notify_observers(self):
        for callback in self._observers:
            callback()

    def _regenerate_plan(self):
        self.plan = self._generate_acquisition_plan()
        self._hash = None
        self._notify_observers()

    def _generate_acquisition_plan(self) -> AcquisitionPlan:
        frame_stacks = self.generate_frame_stacks(self.channels)
        scan_path = self.generate_scan_path(frame_stacks)
        return AcquisitionPlan(frame_stacks, scan_path)

    @property
    def z_step_size(self):
        return self._z_step_size

    @z_step_size.setter
    def z_step_size(self, z_step_size: float):
        self._z_step_size = z_step_size
        self._regenerate_plan()

    @property
    def tile_overlap(self):
        return self._tile_overlap

    @tile_overlap.setter
    def tile_overlap(self, tile_overlap: float):
        self._tile_overlap = tile_overlap
        self._regenerate_plan()

    @enumerated_property(ScanPattern)
    def scan_pattern(self) -> ScanPattern:
        return self._scan_pattern

    @scan_pattern.setter
    def scan_pattern(self, value: ScanPattern):
        self._scan_pattern = value
        self._regenerate_plan()

    @enumerated_property(ScanDirection)
    def scan_direction(self) -> ScanDirection:
        return self._scan_direction

    @scan_direction.setter
    def scan_direction(self, value: ScanDirection):
        self._scan_direction = value
        self._regenerate_plan()

    @enumerated_property(StartCorner)
    def start_corner(self) -> StartCorner:
        return self._start_corner

    @start_corner.setter
    def start_corner(self, value: StartCorner):
        self._start_corner = value
        self._regenerate_plan()

    @property
    def reverse_scan_path(self) -> bool:
        return self._reverse_scan_path

    @reverse_scan_path.setter
    def reverse_scan_path(self, value: bool):
        self._reverse_scan_path = value
        self._regenerate_plan()

    @staticmethod
    def _get_grid_size(frame_stacks) -> Vec2D:
        x_max = max(frame_stack.idx.x for frame_stack in frame_stacks.values())
        y_max = max(frame_stack.idx.y for frame_stack in frame_stacks.values())
        return Vec2D(x_max + 1, y_max + 1)

    def generate_frame_stacks(self, channels: List[VoxelChannel]) -> Dict[Vec2D, FrameStack]:
        channel_names = [channel.name for channel in channels]
        # all channels must have the same fov
        fov = channels[0].fov_um
        for channel in channels:
            if channel.fov_um != fov:
                raise ValueError("Unable to generate tiles with channels of different FOV")
        frame_stacks = {}
        effective_tile_width = fov.x * (1 - self.tile_overlap)
        effective_tile_height = fov.y * (1 - self.tile_overlap)

        x_tiles = math.ceil(self.volume.size.x / effective_tile_width)
        y_tiles = math.ceil(self.volume.size.y / effective_tile_height)

        actual_width = x_tiles * effective_tile_width
        actual_height = y_tiles * effective_tile_height

        for x in range(x_tiles):
            for y in range(y_tiles):
                pos_x = x * effective_tile_width + self.volume.min_corner.x
                pos_y = y * effective_tile_height + self.volume.min_corner.y
                idx = Vec2D(x, y)
                frame_stacks[idx] = FrameStack(
                    idx=idx,
                    pos=Vec3D(pos_x, pos_y, self.volume.min_corner.z),
                    size=Vec3D(effective_tile_width, effective_tile_height, self.volume.size.z),
                    z_step_size=self.z_step_size,
                    channels=channel_names
                )

        self.volume.max_corner.x = self.volume.min_corner.x + actual_width
        self.volume.max_corner.y = self.volume.min_corner.y + actual_height

        return frame_stacks

    def generate_scan_path(self, frame_stacks) -> List[Vec2D]:
        grid_size = self._get_grid_size(frame_stacks)
        match self.scan_pattern:
            case ScanPattern.RASTER:
                path = generate_raster_path(grid_size, self.scan_direction)
            case ScanPattern.SERPENTINE:
                path = generate_serpentine_path(grid_size, self.scan_direction)
            case ScanPattern.SPIRAL:
                path = generate_spiral_path(grid_size)
            case _:
                raise ValueError(f"Unsupported scan pattern: {self.scan_pattern}")
        path = adjust_for_start_corner(path, grid_size, self.start_corner)
        if self.reverse_scan_path:
            path.reverse()
        return path

    def save_to_yaml(self):
        with open(self.file_path, "w") as f:
            yaml = YAML()
            data = {
                "settings": {
                    "z_step_size": self.z_step_size,
                    "tile_overlap": self.tile_overlap,
                    "scan_pattern": self.scan_pattern.name,
                    "scan_direction": self.scan_direction.name,
                    "start_corner": self.start_corner.name,
                    "reverse_scan_path": self.reverse_scan_path,
                    "volume_min_cornter": self.volume.min_corner.to_str(),
                    "volume_max_corner": self.volume.max_corner.to_str()
                },
                "plan": self.plan.to_dict()
            }
            yaml.dump(data, f)

    @classmethod
    def load_from_yaml(cls, instrument: 'VoxelInstrument', file_path: str) -> 'AcquisitionPlanner':
        with open(file_path) as f:
            yaml = YAML()
            data = yaml.load(f)
            settings = data["settings"]
            plan = AcquisitionPlan.from_dict(data["plan"])
            volume_min_corner = Vec3D.from_str(settings["volume_min_cornter"])
            volume_max_corner = Vec3D.from_str(settings["volume_max_corner"])
            planner = cls(
                instrument=instrument,
                z_step_size=settings["z_step_size"],
                channel_names=[channel.name for channel in instrument.channels.values()],
                file_path=file_path,
                tile_overlap=settings["tile_overlap"],
                scan_pattern=ScanPattern[settings["scan_pattern"]],
                scan_direction=ScanDirection[settings["scan_direction"]],
                start_corner=StartCorner[settings["start_corner"]],
                reverse_scan_path=settings["reverse_scan_path"],
                volume_limits_mm=(volume_min_corner, volume_max_corner)
            )
            planner.plan = plan
            return planner

    def __hash__(self):
        if self._hash is None:
            self._hash = hash((
                self.instrument.name,
                self._z_step_size,
                tuple(channel.name for channel in self.channels),
                self.file_path,
                self._tile_overlap,
                self._scan_pattern,
                self._scan_direction,
                self._start_corner,
                self._reverse_scan_path,
                self.volume.min_corner,
                self.volume.max_corner
            ))
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, AcquisitionPlanner):
            return NotImplemented
        return hash(self) == hash(other)

    def __ne__(self, other: 'AcquisitionPlanner') -> bool:
        return not self.__eq__(other)
