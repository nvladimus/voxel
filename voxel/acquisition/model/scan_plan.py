from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Tuple, List, TypeAlias

from voxel.acquisition.model.tile import Tile

Coordinate: TypeAlias = Tuple[int, int]
ScanPath: List[Coordinate]


class StartCorner(Enum):
    TOP_LEFT = 1
    TOP_RIGHT = 2
    BOTTOM_LEFT = 3
    BOTTOM_RIGHT = 4


class Direction(Enum):
    ROW_WISE = 'R'
    COLUMN_WISE = 'C'


class Pattern(Enum):
    SNAKE = 'S'
    DIRECT = 'D'


class ScanPlanStrategy(ABC):
    def __init__(self, reverse: bool = False):
        self.reverse = reverse

    @abstractmethod
    def generate_plan(self, tiles: Dict[Coordinate, Tile]) -> List[Coordinate]:
        pass


class ParametricScanPlan(ScanPlanStrategy):
    def __init__(self, start_corner=StartCorner.TOP_LEFT, direction=Direction.ROW_WISE, pattern=Pattern.DIRECT,
                 reverse: bool = False):
        super().__init__(reverse)
        self.start_corner = start_corner
        self.direction = direction
        self.pattern = pattern

    def generate_plan(self, tiles: Dict[Coordinate, Tile]) -> List[Coordinate]:
        x_tiles = max(t[0] for t in tiles.keys()) + 1
        y_tiles = max(t[1] for t in tiles.keys()) + 1
        scan_plan = []

        i_range = range(x_tiles)
        j_range = range(y_tiles)

        if self.start_corner == StartCorner.TOP_RIGHT:
            i_range = range(x_tiles)
            j_range = range(y_tiles - 1, -1, -1)
        elif self.start_corner == StartCorner.BOTTOM_LEFT:
            i_range = range(x_tiles - 1, -1, -1)
            j_range = range(y_tiles)
        elif self.start_corner == StartCorner.BOTTOM_RIGHT:
            i_range = range(x_tiles - 1, -1, -1)
            j_range = range(y_tiles - 1, -1, -1)

        if self.direction == Direction.ROW_WISE:
            for i in i_range:
                row = [(i, j) for j in j_range]
                if self.pattern == Pattern.SNAKE and i % 2 == 1:
                    row.reverse()
                scan_plan.extend(row)
        elif self.direction == Direction.COLUMN_WISE:
            for j in j_range:
                col = [(i, j) for i in i_range]
                if self.pattern == Pattern.SNAKE and j % 2 == 1:
                    col.reverse()
                scan_plan.extend(col)

        if self.reverse:
            scan_plan.reverse()

        return scan_plan


class CustomScanPlan(ScanPlanStrategy):
    def __init__(self, custom_plan: List[Tuple[int, int]], reverse: bool = False):
        super().__init__(reverse)
        self.custom_plan = custom_plan

    def generate_plan(self, tiles: Dict[Tuple[int, int], Tile]) -> List[Tuple[int, int]]:
        for tile in self.custom_plan:
            if tile not in tiles:
                print(f"Tile {tile} is not in the tile set. Ignoring this tile.")
        scan_plan = [tile for tile in self.custom_plan if tile in tiles]
        if self.reverse:
            scan_plan.reverse()
        return scan_plan


# FIXME: Verify the correctness of this implementation
class SpiralScanPlan(ScanPlanStrategy):
    def generate_plan(self, tiles: Dict[Tuple[int, int], Tile]) -> List[Tuple[int, int]]:
        x_tiles = max(t[0] for t in tiles.keys()) + 1
        y_tiles = max(t[1] for t in tiles.keys()) + 1
        scan_plan = []

        visited = set()
        x, y = 0, 0  # Start from the top-left corner
        dx, dy = 0, -1
        for _ in range(x_tiles * y_tiles):
            if 0 <= x < x_tiles and 0 <= y < y_tiles and (x, y) not in visited:
                scan_plan.append((x, y))
                visited.add((x, y))
            if x + dx == x_tiles or x + dx < 0 or y + dy == y_tiles or y + dy < 0 or (x + dx, y + dy) in visited:
                dx, dy = -dy, dx
            x, y = x + dx, y + dy

        if self.reverse:
            scan_plan.reverse()

        return scan_plan


def visualize_scan_plan(scan_plan: List[Tuple[int, int]]):
    # Create a 2D array to represent the tile plan
    max_i = max(t[0] for t in scan_plan) + 1
    max_j = max(t[1] for t in scan_plan) + 1
    grid = [[' ' for _ in range(max_j)] for _ in range(max_i)]

    # Fill the grid with the tile visitation order
    for order, (i, j) in enumerate(scan_plan):
        grid[i][j] = str(order).zfill(2)

    # Print the grid
    for row in grid:
        print(' '.join(row))
