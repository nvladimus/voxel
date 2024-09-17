from typing import Optional, Dict, List

from acquisition.model.tile_list import YamlTilePersistence, JsonifyTiles, PickleTiles

from acquisition._config import AcquisitionSpecs
from acquisition._definitions import TileAcquisitionStrategy
from acquisition.model import TilePlan, ParametricScanPlan, ScanPlanStrategy
from acquisition.model.volume import Volume
from voxel import VoxelInstrument
from voxel.acquisition.metadata.base import VoxelMetadata
from voxel.utils.logging import get_logger


class VoxelAcquisition:

    def __init__(self,
                 specs: AcquisitionSpecs,
                 instrument: VoxelInstrument,
                 metadata_handler: VoxelMetadata,
                 name: Optional[str] = None
                 ) -> None:
        self.log = get_logger(f"{self.__class__.__name__}")
        self.name = name
        self.specs = specs
        self.instrument = instrument
        self.metadata = metadata_handler
        self.volume = Volume(
            step_size=self.specs.step_size,
            tile_overlap=self.specs.tile_overlap,
            stage_limits_mm=self.instrument.stage.limits_mm
        )
        self.tile_persistence = self._get_tile_persistence_handler()
        self._tiles: Optional[TilePlan] = None
        self.log.debug(f"Acquisition created with instrument: {instrument}")

    @property
    def tiles(self) -> List[TilePlan]:
        match self.specs.strategy:
            case TileAcquisitionStrategy.MULTI_SHOT:
                tile_plans: List[TilePlan] = []
                for channel_name in self.specs.channels:
                    channel = self.instrument.channels.get(channel_name)
                    channel_tiles = self.volume.generate_tiles(
                        channels=[channel],
                        name_prefix=channel_name
                    )
                    tile_plans.append(TilePlan(
                        tiles=channel_tiles,
                        scan_strategy=self.scan_path_strategy,
                    ))
                return tile_plans
            case TileAcquisitionStrategy.ONE_SHOT:
                channels = [self.instrument.channels.get(channel_name) for channel_name in self.specs.channels]
                tile_plans: List[TilePlan] = [
                    TilePlan(
                        tiles=self.volume.generate_tiles(
                            channels=channels,
                            name_prefix="multi_channel"
                        ),
                        scan_strategy=self.scan_path_strategy
                    )]
                return tile_plans

    @property
    def scan_path_strategy(self) -> ScanPlanStrategy:
        match self.specs.scan_path_strategy:
            case "parametric":
                return ParametricScanPlan()
            case "spiral":
                raise NotImplementedError("Spiral scan path strategy not implemented yet")

    def get_metadata(self) -> Dict:
        return self.metadata.to_dict()

    def _get_tile_persistence_handler(self):
        match self.specs.tile_plan_persistence.lower():
            case "yaml":
                return YamlTilePersistence()
            case "json":
                return JsonifyTiles()
            case "pickle":
                return PickleTiles()
