from voxel.instruments.config import InstrumentConfig
from voxel.instruments.factory import InstrumentFactory
from voxel.instruments.instrument import VoxelInstrument

CONFIG_YAML = './instrument_build.yaml'

if __name__ == "__main__":
    from pprint import pprint

    config = InstrumentConfig(CONFIG_YAML)
    factory = InstrumentFactory(config)
    instrument: VoxelInstrument = factory.create_instrument()
    pprint(instrument.cameras)
    pprint(instrument.lasers)
