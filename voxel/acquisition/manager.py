import math
from pprint import pprint
from typing import List, Dict, Callable

from ruamel.yaml import YAML

from voxel import VoxelInstrument
from voxel.acquisition.model.frame_stack import FrameStack
from voxel.acquisition.model.plan import VoxelAcquisitionPlan
from voxel.acquisition.model.scan_path import (
    ScanPattern, ScanDirection, StartCorner,
    generate_raster_path, generate_serpentine_path,
    generate_spiral_path, adjust_for_start_corner
)
from voxel.acquisition.model.specs import AcquisitionSpecs
from voxel.acquisition.model.volume import Volume
from voxel.instrument.channel import VoxelChannel
from voxel.utils.descriptors.enumerated_property import enumerated_property
from voxel.utils.geometry.vec import Vec2D, Vec3D
from voxel.utils.logging import get_logger

DEFAULT_TILE_OVERLAP = 0.15


def clean_yaml_file(file_path: str) -> None:
    # remove extra newlines at the end of each section
    with open(file_path) as f:
        lines = f.readlines()
    with open(file_path, 'w') as f:
        f.writelines([line for line in lines if line.strip() != ""])


class VoxelAcquisitionManager:
    def __init__(
            self,
            instrument: 'VoxelInstrument',
            specs: AcquisitionSpecs,
            channel_names: List[str] = 'all',
            plan: VoxelAcquisitionPlan = None
    ) -> None:
        self.log = get_logger(self.__class__.__name__)
        self.instrument = instrument
        self._specs = specs

        self._z_step_size = self._specs.z_step_size
        self._tile_overlap = self._specs.tile_overlap
        self._scan_pattern = ScanPattern(self._specs.scan_pattern)
        self._scan_direction = ScanDirection(self._specs.scan_direction)
        self._start_corner = StartCorner(self._specs.start_corner)
        self._reverse_scan_path = self._specs.reverse_scan_path
        self._file_path = self._specs.file_path

        if channel_names == 'all':
            self.channels = list(instrument.channels.values())
        else:
            self.channels = [instrument.channels[channel_name] for channel_name in channel_names]

        self._observers: List[Callable[[], None]] = []
        self._hash = None

        if self._specs.volume_min_corner:
            volume_min_corner = Vec3D.from_str(self._specs.volume_min_corner)
        else:
            volume_min_corner = instrument.stage.limits_mm[0]
            self._specs.volume_min_corner = volume_min_corner.to_str()
        if self._specs.volume_max_corner:
            volume_max_corner = Vec3D.from_str(self._specs.volume_max_corner)
        else:
            volume_max_corner = instrument.stage.limits_mm[1]
            self._specs.volume_max_corner = volume_max_corner.to_str()

        self.volume = Volume(volume_min_corner, volume_max_corner, self.z_step_size)
        self.volume.add_observer(self._regenerate_plan)

        self.plan = plan or self._generate_acquisition_plan()

    def add_observer(self, callback: Callable[[], None]):
        self._observers.append(callback)

    def _notify_observers(self):
        for callback in self._observers:
            callback()

    def _regenerate_plan(self):
        self.plan = self._generate_acquisition_plan()
        self._hash = None
        self._notify_observers()

    def _generate_acquisition_plan(self) -> VoxelAcquisitionPlan:
        frame_stacks = self.generate_frame_stacks(self.channels)
        scan_path = self.generate_scan_path(frame_stacks)
        return VoxelAcquisitionPlan(frame_stacks, scan_path)

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

    def save_to_yaml(self) -> None:
        self.log.info(f"Saving acquisition to {self._file_path}")
        specs = {
            "z_step_size": self.z_step_size,
            "tile_overlap": self.tile_overlap,
            "scan_pattern": str(self.scan_pattern),
            "scan_direction": str(self.scan_direction),
            "start_corner": str(self.start_corner),
            "reverse_scan_path": self.reverse_scan_path,
            "volume_min_corner": self.volume.min_corner.to_str(),
            "volume_max_corner": self.volume.max_corner.to_str(),
            "file_path": self._file_path,
        }
        channels = [channel.name for channel in self.channels]

        clean_yaml_file(self._file_path)

        yaml = YAML()
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)

        # Read existing content
        try:
            with open(self._file_path) as file:
                data = yaml.load(file) or {}
        except FileNotFoundError:
            data = {}

        # Update the necessary keys
        data["specs"] = specs
        data["channels"] = channels
        data["plan"] = self.plan.to_dict()

        # Write updated content back to file
        with open(self._file_path, 'w') as file:
            for key, value in data.items():
                yaml.dump({key: value}, file)
                file.write("\n")

    @classmethod
    def load_from_yaml(cls, instrument: 'VoxelInstrument', file_path: str) -> 'VoxelAcquisitionManager':
        with open(file_path) as f:
            yaml = YAML()
            data = yaml.load(f)
            print("Loaded YAML data:")
            pprint(data)

            specs_data = data.get("specs", {})
            specs_data['file_path'] = file_path

            try:
                specs = AcquisitionSpecs(**specs_data)
            except Exception as e:
                print(f"Error constructing AcquisitionSpecs: {e}")
                raise

            plan = VoxelAcquisitionPlan.from_dict(data["plan"])
            planner = cls(
                instrument=instrument,
                specs=specs,
                channel_names=data["channels"],
            )
            planner.plan = plan
            return planner

    def __hash__(self):
        if self._hash is None:
            self._hash = hash((
                self.instrument.name,
                self._z_step_size,
                tuple(channel.name for channel in self.channels),
                self._file_path,
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
        if not isinstance(other, VoxelAcquisitionManager):
            return NotImplemented
        return hash(self) == hash(other)

    def __ne__(self, other: 'VoxelAcquisitionManager') -> bool:
        return not self.__eq__(other)
