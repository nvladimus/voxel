from abc import ABC, abstractmethod
from enum import Enum
import logging
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Process, Queue
from pathlib import Path
from typing import Self


class LogColor(Enum):
    """ANSI color codes for logging"""

    GREY = "\033[38;20m"
    BLUE = "\033[34;20m"
    YELLOW = "\033[33;20m"
    RED = "\033[31;20m"
    BOLD_RED = "\033[31;1m"
    GREEN = "\033[32;20m"
    CYAN = "\033[36;20m"
    PURPLE = "\033[35;20m"
    RESET = "\033[0m"


class CustomFormatter(logging.Formatter):
    """Base formatter with common functionality"""

    LEVEL_EMOJIS: dict[int, str] = {
        logging.DEBUG: "🔍",
        logging.INFO: "⚡️",
        logging.WARNING: "⚠️ ",
        logging.ERROR: "❌",
        logging.CRITICAL: "🚨",
    }

    LEVEL_COLORS: dict[int, LogColor] = {
        logging.DEBUG: LogColor.PURPLE,
        logging.INFO: LogColor.BLUE,
        logging.WARNING: LogColor.YELLOW,
        logging.ERROR: LogColor.RED,
        logging.CRITICAL: LogColor.BOLD_RED,
    }

    def __init__(self, detailed: bool = True, fancy: bool = False, colored: bool = True) -> None:
        self.detailed = detailed
        self.fancy = fancy
        self.colored = colored

        date_fmt = "%Y-%m-%d %H:%M:%S"
        level_str = "%(emoji)s" if self.fancy else "%(levelname)8s"

        default_fmt = f"%(asctime)s - {level_str} - %(name)-25s - %(message)-42s"
        default_fmt = f"%(color_code)s{default_fmt}{LogColor.RESET.value}" if self.colored else default_fmt

        file_name = "%(filename)s:%(lineno)d"
        file_name = f"{LogColor.CYAN.value}{file_name}{LogColor.RESET.value}" if self.colored else file_name

        process_name = "%(processName)s"
        process_name = f"%(color_code)s{process_name}{LogColor.RESET.value}" if self.colored else process_name

        detailed_fmt = default_fmt + f" - {file_name} - {process_name}"
        super().__init__(fmt=detailed_fmt if detailed else default_fmt, datefmt=date_fmt)

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with emojis"""
        if self.fancy:
            record.emoji = self.LEVEL_EMOJIS.get(record.levelno, "-")
        if self.colored:
            record.color_code = self.LEVEL_COLORS.get(record.levelno, LogColor.GREY).value
        return super().format(record)

    def formatException(self, exc_info) -> str:
        """Format exception with red color"""
        if exc_info:
            formatted = super().formatException(exc_info)
            if self.fancy:
                return f"{self.emojis.ERROR} {formatted}"
            return formatted
        return ""


LOGGING_SUBPROC_SUFFIX = "_subprocess"
LOGGING_PROJECT_NAME = "voxel"
LOG_QUEUE = Queue(-1)


def get_logger(name) -> logging.Logger:
    """
    Get a logger with the given name, ensuring it's a child of the 'voxel' logger.

    :param name: The name of the logger.
    :return: A Logger instance.
    """
    return logging.getLogger(f"{LOGGING_PROJECT_NAME}.{name}")


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


class VoxelLogging:
    """Context manager for setting up logging"""

    def __init__(
        self,
        level: str = "INFO",
        log_file: str | None = None,
        fancy: bool = True,
        detailed: bool = True,
    ) -> None:
        """Initialize logging configuration
        :param level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        :param log_file: Optional path to log file
        :param fancy: Whether to use emoji and color formatting
        """
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.log_file = log_file
        self.fancy = fancy
        self.detailed = detailed
        self.listener = None
        self.handlers = []
        self.queue_handler = None

        # Get root and library loggers
        self.root_logger = logging.getLogger()
        self.lib_logger = logging.getLogger(LOGGING_PROJECT_NAME)

    def _create_handlers(self) -> list:
        """Create and configure log handlers"""
        handlers = []

        # Create formatters
        console_formatter = CustomFormatter(detailed=self.detailed, fancy=self.fancy, colored=True)
        file_formatter = CustomFormatter(detailed=self.detailed, fancy=False, colored=False)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)

        # File handler if log file specified
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)

        return handlers

    def __enter__(self) -> Self:
        """Set up logging when entering context"""
        # Clear existing handlers
        self.root_logger.handlers.clear()
        self.lib_logger.handlers.clear()

        # Set levels
        self.root_logger.setLevel(self.level)
        self.lib_logger.setLevel(self.level)

        # Create handlers
        self.handlers = self._create_handlers()

        # Create a QueueHandler and add it to the root logger
        self.queue_handler = QueueHandler(LOG_QUEUE)
        self.root_logger.addHandler(self.queue_handler)

        # Always set up queue listener for subprocess logging
        self.listener = QueueListener(LOG_QUEUE, *self.handlers, respect_handler_level=True)
        self.listener.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up logging when exiting context"""
        if self.listener:
            self.listener.stop()
        if self.queue_handler:
            self.root_logger.removeHandler(self.queue_handler)


def with_logging(level: str = "INFO", log_file: str | None = None, fancy: bool = True):
    """decorator to run a function with logging"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            with VoxelLogging(level=level, log_file=log_file, fancy=fancy):
                return func(*args, **kwargs)

        return wrapper

    return decorator


class LoggingSubprocess(Process, ABC):
    """
    Abstract base process class that handles logging setup for child processes.
    """

    def __init__(self, name: str, queue: Queue = LOG_QUEUE) -> None:
        super().__init__()
        self.name = name
        self._log_queue = queue
        self._log_level = logging.getLogger().getEffectiveLevel()
        self.log = get_component_logger(self)
        self._initialized = False

    def _setup_logging(self):
        """Set up logging for the subprocess"""
        if not self._initialized:
            self.log = get_component_logger(self)
            self.name += LOGGING_SUBPROC_SUFFIX

            root_logger = logging.getLogger()
            lib_logger = logging.getLogger(LOGGING_PROJECT_NAME)
            loggers = [root_logger, lib_logger]

            [logger.handlers.clear() for logger in loggers]

            queue_handler = QueueHandler(self._log_queue)
            root_logger.addHandler(queue_handler)

            [logger.setLevel(self._log_level) for logger in loggers]

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


# Example usage
class Counter(LoggingSubprocess):
    def __init__(self, name: str, count: int):
        super().__init__(name)
        self.count = count

    def _run(self):
        import time

        self.log.info(f"Counter process started with count={self.count}")  # Added startup message
        for i in range(self.count):
            self.log.info(f"Count: {i}")
            time.sleep(0.5)  # Reduced sleep time for faster testing
        self.log.info("Counter process completed")  # Added completion message


@with_logging()
def main() -> None:
    proc = Counter("counter", 5)
    proc.log.critical("Main process started ....................................")
    proc.log.info("Starting counter process")
    proc.start()
    proc.join()
    proc.log.warning("Counter process joined")
    proc.log.error("Counter process exited")


if __name__ == "__main__":
    main()
