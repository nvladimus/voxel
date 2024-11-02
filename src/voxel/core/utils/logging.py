from abc import ABC, abstractmethod
from enum import IntEnum
import logging
import logging.config
from logging.handlers import QueueListener
from multiprocessing import Process, Queue
from typing import Callable

custom_date_format = "%Y-%m-%d %H:%M:%S"

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s - %(levelname)8s - %(name)35s: %(message)s", "datefmt": custom_date_format},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "voxel": {  # Root voxel logger
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

log_level = "INFO"


def setup_logging(config=None, level="INFO", log_file=None) -> None:
    """
    Set up logging configuration for the library.
    """
    logging_config = config or DEFAULT_LOGGING_CONFIG
    if level:
        log_level = level

    logging_config["loggers"]["voxel"]["level"] = log_level

    if log_file:
        logging_config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": log_file,
            "mode": "a",
        }
        logging_config["loggers"]["voxel"]["handlers"].append("file")

    logging.config.dictConfig(logging_config)

    # Set the log level for any existing loggers
    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("voxel"):
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.getLevelName(log_level))
            # Also set the level for all handlers
            for handler in logger.handlers:
                handler.setLevel(logging.getLevelName(log_level))


def setup_subprocess_queue_logging(queue: Queue) -> None:
    """
    Set up logging configuration for child processes using queue handler
    while maintaining consistent formatting.
    """
    # Remove any existing handlers
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Add queue handler without formatting - formatting will be done by main process
    handler = logging.handlers.QueueHandler(queue)
    root.addHandler(handler)

    # Set level
    root.setLevel(logging.getLevelName(log_level))

    # Configure voxel logger
    logger = logging.getLogger("voxel")
    logger.setLevel(logging.getLevelName(log_level))
    logger.propagate = False

    # Remove any existing handlers and add queue handler
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    logger.addHandler(handler)


def get_logger(name) -> logging.Logger:
    """
    Get a logger with the given name, ensuring it's a child of the 'voxel' logger.

    :param name: The name of the logger.
    :return: A Logger instance.
    """
    return logging.getLogger(f"voxel.{name}")


def get_component_logger(obj: object) -> logging.Logger:
    """
    Get a logger for a specific component.

    :param obj: The component object for which to get the logger.
    :return: A Logger instance.
    """
    if hasattr(obj, "name"):
        if isinstance(obj.name, str) and obj.name != "":
            return get_logger(f"{obj.__class__.__name__}[{obj.name}]")
    return get_logger(obj.__class__.__name__)


log_queue = Queue()


def get_subprocess_log_queue() -> Queue:
    """
    Singleton function to get the log queue for subprocesses.
    """
    return log_queue


class LoggingSubprocess(Process, ABC):
    """
    Abstract base process class that handles logging setup for child processes.
    """

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.log = get_component_logger(self)
        self.log_queue = get_subprocess_log_queue()
        self._initialized = False

    def _setup_logging(self):
        """Set up logging for the subprocess"""
        if not self._initialized:
            setup_subprocess_queue_logging(self.log_queue)
            # Refresh logger after subprocess setup
            self.name += "_subprocess"
            self.log = get_component_logger(self)
            self._initialized = True

    def run(self) -> None:
        """
        Main process execution method. Sets up logging and calls _run().
        Child classes should override _run() instead of run().
        """
        try:
            self._setup_logging()
            self._run()
        except Exception as e:
            self.log.error(f"Process error: {str(e)}", exc_info=True)
            raise e

    @abstractmethod
    def _run(self) -> None:
        """
        Main process execution logic. Must be implemented by child classes.
        """
        pass


def run_with_logging(func: Callable, level="INFO", subprocess: bool = False) -> None:
    """
    Run a function with logging setup.
    """
    setup_logging(level=level)
    if subprocess:
        handlers = logging.getLogger("voxel").handlers
        listener = QueueListener(log_queue, *handlers, respect_handler_level=True)
        listener.start()
        try:
            func()
        finally:
            listener.stop()
    else:
        func()
