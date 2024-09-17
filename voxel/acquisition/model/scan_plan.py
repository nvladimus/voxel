from abc import ABC, abstractmethod
from enum import Enum, StrEnum
from typing import List, Tuple, TypeAlias

from colorama import init

from voxel.acquisition.model.tile import TilesSet, Coordinate
from voxel.utils.logging import get_logger

init(autoreset=True)  # Initialize colorama

ScanPath: TypeAlias = List[Coordinate]


class StartCorner(StrEnum):
    TOP_LEFT = 'top_left'
    TOP_RIGHT = 'top_right'
    BOTTOM_LEFT = 'bottom_left'
    BOTTOM_RIGHT = 'bottom_right'


class Direction(Enum):
    ROW_WISE = 'row_wise'
    COLUMN_WISE = 'column_wise'
    CLOCKWISE = 'clockwise'
    COUNTERCLOCKWISE = 'counterclockwise'


class Pattern(Enum):
    SERPENTINE = 'serpentine'
    RASTER = 'raster'


class ScanPathStrategy(StrEnum):
    PARAMETRIC = 'parametric'
    SPIRAL = 'spiral'
    CUSTOM = 'custom'


class ScanPathGenerator(ABC):
    def __init__(self) -> None:
        self.log = get_logger(self.__class__.__name__)

    def generate_path(self, tiles: List[TilesSet]) -> ScanPath:
        """Generate a scan path for all tile sets."""
        path = []
        for tile_set in tiles:
            path.extend(self._generate_scan_path(tile_set))
        return path

    @abstractmethod
    def _generate_scan_path(self, tiles: TilesSet) -> ScanPath:
        """Generate a scan path for a single tile set."""
        pass


class ParametricScanPathGenerator(ScanPathGenerator):
    def __init__(self, start_corner: StartCorner, direction: Direction, pattern: Pattern,
                 reverse: bool = False) -> None:
        super().__init__()
        self.start_corner: StartCorner = start_corner
        self.direction: Direction = direction
        self.pattern: Pattern = pattern
        self.reverse: bool = reverse

    def _generate_scan_path(self, tiles: TilesSet) -> ScanPath:
        x_tiles = max(t[0] for t in tiles.keys()) + 1
        y_tiles = max(t[1] for t in tiles.keys()) + 1
        scan_plan = []

        i_range, j_range = self._get_ranges(x_tiles, y_tiles)

        if self.direction == Direction.COLUMN_WISE:
            for i in i_range:
                row = [(i, j) for j in j_range]
                if self.pattern == Pattern.SERPENTINE and i % 2 == 1:
                    row.reverse()
                scan_plan.extend(row)
        else:
            for j in j_range:
                col = [(i, j) for i in i_range]
                if self.pattern == Pattern.SERPENTINE and j % 2 == 1:
                    col.reverse()
                scan_plan.extend(col)

        if self.reverse:
            scan_plan.reverse()

        return scan_plan

    def _get_ranges(self, x_tiles: int, y_tiles: int) -> Tuple[range, range]:
        if self.start_corner == StartCorner.TOP_LEFT:
            return range(x_tiles), range(y_tiles)
        elif self.start_corner == StartCorner.TOP_RIGHT:
            return range(x_tiles), range(y_tiles - 1, -1, -1)
        elif self.start_corner == StartCorner.BOTTOM_LEFT:
            return range(x_tiles - 1, -1, -1), range(y_tiles)
        elif self.start_corner == StartCorner.BOTTOM_RIGHT:
            return range(x_tiles - 1, -1, -1), range(y_tiles - 1, -1, -1)


class SpiralScanPathGenerator(ScanPathGenerator):
    def __init__(self, start_corner: StartCorner = StartCorner.TOP_LEFT,
                 direction: Direction = Direction.CLOCKWISE,
                 reverse: bool = False) -> None:
        super().__init__()
        self.start_corner = start_corner
        self.direction = direction
        self.reverse = reverse

    def _generate_scan_path(self, tiles: TilesSet) -> ScanPath:
        x_tiles = max(t[0] for t in tiles.keys()) + 1
        y_tiles = max(t[1] for t in tiles.keys()) + 1
        scan_plan = []

        visited = set()
        x, y = self._get_start_position(x_tiles, y_tiles)
        dx, dy = self._get_initial_direction()

        for _ in range(x_tiles * y_tiles):
            if 0 <= x < x_tiles and 0 <= y < y_tiles and (x, y) not in visited:
                scan_plan.append((x, y))
                visited.add((x, y))
            if (x + dx == x_tiles or x + dx < 0 or
                    y + dy == y_tiles or y + dy < 0 or
                    (x + dx, y + dy) in visited):
                dx, dy = self._rotate_direction(dx, dy)
            x, y = x + dx, y + dy

        if self.reverse:
            scan_plan.reverse()

        self.log.debug(f"Generated spiral path with {len(scan_plan)} tiles")
        return scan_plan

    def _get_start_position(self, x_tiles: int, y_tiles: int) -> Tuple[int, int]:
        if self.start_corner == StartCorner.TOP_LEFT:
            return 0, 0
        elif self.start_corner == StartCorner.TOP_RIGHT:
            return x_tiles - 1, 0
        elif self.start_corner == StartCorner.BOTTOM_LEFT:
            return 0, y_tiles - 1
        elif self.start_corner == StartCorner.BOTTOM_RIGHT:
            return x_tiles - 1, y_tiles - 1

    def _get_initial_direction(self) -> Tuple[int, int]:
        if self.start_corner == StartCorner.TOP_LEFT:
            return (1, 0) if self.direction == Direction.CLOCKWISE else (0, 1)
        elif self.start_corner == StartCorner.TOP_RIGHT:
            return (0, 1) if self.direction == Direction.CLOCKWISE else (-1, 0)
        elif self.start_corner == StartCorner.BOTTOM_LEFT:
            return (0, -1) if self.direction == Direction.CLOCKWISE else (1, 0)
        elif self.start_corner == StartCorner.BOTTOM_RIGHT:
            return (-1, 0) if self.direction == Direction.CLOCKWISE else (0, -1)

    def _rotate_direction(self, dx: int, dy: int) -> Tuple[int, int]:
        return (-dy, dx) if self.direction == Direction.CLOCKWISE else (dy, -dx)


class CustomScanPathGenerator(ScanPathGenerator):
    def __init__(self, custom_plan: List[Coordinate]) -> None:
        super().__init__()
        self.custom_plan: List[Coordinate] = custom_plan

    def _generate_scan_path(self, tiles: TilesSet) -> ScanPath:
        return [tile for tile in self.custom_plan if tile in tiles]
