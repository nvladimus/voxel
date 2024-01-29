import array
import logging
import numpy as np
import os
import tifffile
from multiprocessing import Process, Value, Event, Array
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path

class BackgroundCollection(Process):

    def __init__(self):

        super().__init__()
