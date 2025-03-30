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


def setup_logger(config_manager):
    """Configure and return logger instance"""
    log_file = config_manager.get_log_file()

    logger = logging.getLogger("FolderReplicator")
    logger.setLevel(logging.INFO)

    # Clear existing handlers if any
    if logger.handlers:
        logger.handlers = []

    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
