import numpy
import time
import math
import threading
import logging
import sys
from pathlib import Path
from spim_core.config_base import Config
from threading import Event, Thread
from instrument import Instrument
from acquisition import Acquisition
from writers.data_structures.shared_double_buffer import SharedDoubleBuffer
from multiprocessing.shared_memory import SharedMemory
from writers.imaris import Writer

if __name__ == '__main__':

    # Setup logging.
    # Create log handlers to dispatch:
    # - User-specified level and above to print to console if specified.
    logger = logging.getLogger()  # get the root logger.
    # Remove any handlers already attached to the root logger.
    logging.getLogger().handlers.clear()
    # logger level must be set to the lowest level of any handler.
    logger.setLevel(logging.DEBUG)
    fmt = '%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s'
    datefmt = '%Y-%m-%d,%H:%M:%S'
    log_formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setLevel('INFO')
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)

    # instrument
    instrument = Instrument('simulated_instrument.yaml')

    # acquisition
    acquisition = Acquisition(instrument, 'test_acquisition.yaml')
    acquisition.check_disk_space()
    acquisition.check_system_memory()
    acquisition.run()