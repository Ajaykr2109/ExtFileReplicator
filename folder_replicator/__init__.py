from folder_replicator.config_manager import ConfigManager
from folder_replicator.synchronization import Synchronizer
from folder_replicator.watcher import ReplicationWatcher
from folder_replicator.cli import main
from folder_replicator.logger import setup_logger
from folder_replicator.gui import MainWindow, run_gui

__version__ = "1.1.1"

__all__ = [
    'ConfigManager',
    'Synchronizer',
    'ReplicationWatcher',
    'main',
    'setup_logger',
    'MainWindow',
    'run_gui',
]
