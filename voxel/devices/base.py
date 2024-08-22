"""Base class for all voxel devices."""
import sys
from abc import ABC, abstractmethod
import logging


class VoxelDevice(ABC):
    """Base class for all voxel devices."""

    _logging_configured = False

    def __init__(self, id: str):
        """Initialize the device.
        :param id: The unique identifier of the device.
        :type id: str
        """
        self.id = id
        self.log = logging.getLogger(f'{self.__class__.__name__}[{self.id}]')

        # Ensure logging is configured
        self.configure_logging()

    @abstractmethod
    def close(self):
        """Close the device."""
        pass

    def __str__(self):
        return self.__repr__()

    @classmethod
    def configure_logging(cls):
        if not cls._logging_configured:
            custom_log_format = '%(asctime)s - %(levelname)8s - %(name)28s: %(message)s'
            custom_date_format = '%Y-%m-%d %H:%M:%S'

            formatter = logging.Formatter(fmt=custom_log_format, datefmt=custom_date_format)

            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)

            # Remove any existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

            cls._logging_configured = True


class DeviceConnectionError(Exception):
    """Custom exception for camera discovery errors."""
    pass
