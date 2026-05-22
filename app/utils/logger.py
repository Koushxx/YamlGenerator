"""
Logging utility for the application.
"""

import os
import logging
from datetime import datetime


def setup_logger(log_dir: str = None) -> logging.Logger:
    """
    Set up application logger with file and console handlers.
    """
    if log_dir is None:
        log_dir = os.path.join(os.path.expanduser("~"), ".device_yaml_generator", "logs")

    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

    logger = logging.getLogger("DeviceYAMLGenerator")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
