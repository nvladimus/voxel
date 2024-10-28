import logging
import logging.config

custom_date_format = "%Y-%m-%d %H:%M:%S"

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s - %(levelname)8s - %(name)45s: %(message)s", "datefmt": custom_date_format},
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


def setup_logging(config=None, log_level="INFO", log_file=None):
    """
    Set up logging configuration for the library.

    :param config: A dictionary of logging configuration. If provided, it will override the default configuration.
    :param log_level: If provided, it will override the log level for the 'voxel' logger.
    :param log_file: If provided, it will add a FileHandler to the 'voxel' logger.
    """
    logging_config = config or DEFAULT_LOGGING_CONFIG

    if log_level:
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


def get_logger(name):
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
