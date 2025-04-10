import logging
import os
from pathlib import Path
import platform
import sys
from datetime import datetime


def getUserLogDir():
    system = platform.system()
    if system == "Windows":
        log_dir = Path(os.environ.get('LOCALAPPDATA', '')) / \
            "FolderReplicator" / "Logs"
    elif system == "Darwin":
        log_dir = Path.home() / "Library" / "Logs" / "FolderReplicator"
    else:
        log_dir = Path.home() / ".local" / "share" / "FolderReplicator" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logger(config_manager, quiet=False, verbose=False):
    """Configure and return logger instance"""
    log_file = config_manager.get_log_file()
    config = config_manager.get_config()
    log_level = getattr(logging, config.get('log_level', 'INFO'))

    # Adjust log level based on flags
    if quiet:
        log_level = logging.ERROR
    elif verbose:
        log_level = logging.DEBUG

    logger = logging.getLogger("FolderReplicator")
    logger.setLevel(log_level)

    if logger.handlers:
        logger.handlers = []

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
