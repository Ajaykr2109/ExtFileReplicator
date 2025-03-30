import logging
import os
from pathlib import Path
import platform
from datetime import datetime


def get_user_log_dir():
    """Get platform-specific user log directory"""
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


def setup_logger():
    """Configure and return logger instance"""
    log_dir = get_user_log_dir()
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"folder_replicator_{current_date}.log"

    logger = logging.getLogger("FolderReplicator")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
