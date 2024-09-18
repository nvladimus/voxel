import json
import pickle
from abc import abstractmethod, ABC
from typing import Tuple, List

from ruamel.yaml import YAML

from voxel.acquisition._prev.scan_plan import ScanPath
from voxel.acquisition._prev.tile import TilesSet, Tile


class TilePersistenceHandler(ABC):
    def __init__(self, file_path: str):
        self.file_path = file_path

    @abstractmethod
    def save_tiles(self, tiles: List[TilesSet], scan_path: ScanPath) -> None:
        pass

    @abstractmethod
    def load_tiles(self) -> Tuple[List[TilesSet], ScanPath]:
        pass


class PickleTiles(TilePersistenceHandler):
    def save_tiles(self, tiles: List[TilesSet], scan_path: ScanPath) -> None:
        with open(self.file_path, 'wb') as f:
            pickle.dump({'tiles': tiles, 'scan_path': scan_path}, f)

    def load_tiles(self) -> Tuple[List[TilesSet], ScanPath]:
        with open(self.file_path, 'rb') as f:
            data = pickle.load(f)
            return data["tiles"], data["scan_path"]


def _stringify_scan_path(scan_path: ScanPath) -> str:
    return " ".join([f"({coord[0]},{coord[1]})" for coord in scan_path])


def _parse_scan_path(scan_path_str: str) -> ScanPath:
    return [(int(coord[1]), int(coord[3])) for coord in scan_path_str.split()]


class YamlifyTiles(TilePersistenceHandler):
    def save_tiles(self, tiles: List[TilesSet], scan_path: ScanPath) -> None:
        with open(self.file_path, 'w') as f:
            tiles_data = []
            for tile_set in tiles:
                tiles_data.append({str(k): v.to_dict() for k, v in tile_set.items()})
            yaml = YAML()
            yaml.dump({'scan_path': _stringify_scan_path(scan_path), 'tiles': tiles_data}, f)

    def load_tiles(self) -> Tuple[List[TilesSet], ScanPath]:
        with open(self.file_path) as f:
            yaml = YAML()
            data = yaml.load(f)
            tiles = [{eval(k): Tile.from_dict(v) for k, v in tile_set.items()} for tile_set in data["tiles"]]
            return tiles, _parse_scan_path(data["scan_path"])


class JsonifyTiles(TilePersistenceHandler):
    def save_tiles(self, tiles: List[TilesSet], scan_path: ScanPath) -> None:
        with open(self.file_path, 'w') as f:
            tiles_data = []
            for tile_set in tiles:
                tiles_data.append({str(k): v.to_dict() for k, v in tile_set.items()})
            json.dump({'scan_path': _stringify_scan_path(scan_path), 'tiles': tiles_data}, f)

    def load_tiles(self) -> Tuple[List[TilesSet], ScanPath]:
        with open(self.file_path) as f:
            data = json.load(f)
            tiles = [{eval(k): Tile.from_dict(v) for k, v in tile_set.items()} for tile_set in data["tiles"]]
            return tiles, _parse_scan_path(data["scan_path"])
