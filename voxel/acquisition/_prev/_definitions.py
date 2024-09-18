from enum import StrEnum


class TileAcquisitionStrategy(StrEnum):
    """Tile acquisition strategies. \n
    Defines how acquisition is performed on a tile basis with multiple channels.
    """
    ONE_SHOT = 'one_shot'
    MULTI_SHOT = 'multi_shot'
