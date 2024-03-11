import array
import logging
import numpy as np
import os
import tifffile
from pathlib import Path

class BackgroundCollection:

    def __init__(self):

        super().__init__()
        self._frame_count_px = 1

    @property
    def frame_count_px(self):
        return self._frame_count_px

    @frame_count_px.setter
    def frame_count_px(self, frame_count_px: int):
        self._frame_count_px = frame_count_px

