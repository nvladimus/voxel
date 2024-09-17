import json
import pickle
from abc import abstractmethod, ABC
from typing import Tuple, List

from ruamel.yaml import YAML

from voxel.acquisition.model.tile import TilePlan
from voxel.acquisition.model.scan_plan import ScanPath
from voxel.acquisition.model.tile import Tile


class TileListPersistence(ABC):
    @abstractmethod
    def save_tiles(self, tiles: List[TilePlan], scan_path: ScanPath, file_path: str) -> None:
        pass

    @abstractmethod
    def load_tiles(self, file_path: str) -> Tiles:
        pass


class JsonifyTiles(TileListPersistence):
    def save_tiles(self, tiles: List[TilePlan], scan_path: ScanPath, file_path: str) -> None:
        with open(file_path, 'w') as f:
            tiles = {str(k): v.__dict__ for k, v in tiles.items()}
            json.dump({'tiles': tiles, 'scan_path': scan_path}, f, indent=2)

    def load_tiles(self, file_path: str) -> Tuple[Tiles, ScanPath]:
        with open(file_path) as f:
            data = json.load(f)
            tiles = {eval(k): Tile(**v) for k, v in data["tiles"].items()}
            return tiles, data["scan_path"]


class YamlTilePersistence(TileListPersistence):
    def save_tiles(self, tiles: List[TilePlan], scan_path: ScanPath, file_path: str) -> None:
        with open(file_path, 'w') as f:
            tiles = {str(k): v.__dict__ for k, v in tiles.items()}
            yaml = YAML()
            yaml.dump({'tiles': tiles, 'scan_path': scan_path}, f)

    def load_tiles(self, file_path: str) -> Tuple[Tiles, ScanPath]:
        with open(file_path) as f:
            yaml = YAML()
            data = yaml.load(f)
            tiles = {eval(k): Tile(**v) for k, v in data["tiles"].items()}
            return tiles, data["scan_path"]


class PickleTiles(TileListPersistence):
    def save_tiles(self, tiles: Tiles, scan_path: ScanPath, file_path: str) -> None:
        with open(file_path, 'wb') as f:
            pickle.dump({'tiles': tiles, 'scan_path': scan_path}, f)

    def load_tiles(self, file_path: str) -> Tuple[Tiles, ScanPath]:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            return data["tiles"], data["scan_path"]
