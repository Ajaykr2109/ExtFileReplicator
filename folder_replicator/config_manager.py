import json
import os
from pathlib import Path
from datetime import datetime
import platform
from typing import Dict, Any, List, Union, Optional


class ConfigManager:
    def __init__(self, config_file='replicator_config.json'):
        self.config_file = config_file
        self.config = self._load_config()
        self._log_dir = self._init_log_dir()

    def _init_log_dir(self) -> Path:
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

    def _load_config(self) -> Dict[str, Any]:
        default_config = {
            "replications": [],
            "sync_interval": 60,
            "log_level": "INFO",
            "max_log_size": 10
        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Ensure all required keys exist
                    for key in default_config:
                        if key not in loaded_config:
                            loaded_config[key] = default_config[key]
                    return loaded_config
        except Exception as e:
            print(f"Error loading config: {e}")
        return default_config.copy()

    def save_config(self) -> bool:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def add_replication(self, source: str, destination: str, exclusions: Optional[List[str]] = None) -> bool:
        try:
            source = str(Path(source).resolve())
            destination = str(Path(destination).resolve())

            if not os.path.exists(source):
                raise FileNotFoundError(
                    f"Source folder does not exist: {source}")

            for replication in self.config['replications']:
                if replication['source'] == source:
                    raise ValueError(
                        f"Replication with the source already exists: {source} | use 'frep list' to see all replications")
                if replication['source'] == destination and replication['destination'] == source:
                    raise ValueError(
                        f"Replication with destination as source and source as destination already exists: {destination} -> {source} | use 'frep list' to see all replications")

            replication = {
                'source': source,
                'destination': destination,
                'last_sync': None,
                'exclusions': exclusions or []
            }

            self.config['replications'].append(replication)
            return self.save_config()
        except Exception as e:
            print(f"Error adding replication: {e}")
            return False

    def get_replications(self) -> List[Dict[str, Any]]:
        return self.config.get('replications', [])

    def update_last_sync(self, replication_index: int, timestamp: float) -> bool:
        try:
            if 0 <= replication_index < len(self.config['replications']):
                self.config['replications'][replication_index]['last_sync'] = datetime.fromtimestamp(
                    timestamp).strftime('%Y-%m-%d %H:%M:%S')
                return self.save_config()
            return False
        except Exception as e:
            print(f"Error updating last sync: {e}")
            return False

    def remove_replication(self, source_path: str) -> bool:
        self.config['replications'] = [r for r in self.config['replications']
                                       if r['source'] != source_path]
        return self.save_config()

    def set_config(self, option: str, value: Union[int, str, float]) -> bool:
        if not isinstance(self.config, dict):
            self.config = self._load_config()

        valid_options = ['sync_interval', 'log_level', 'max_log_size']
        if option not in valid_options:
            return False

        try:
            if option == 'sync_interval':
                value = int(value)
                if value <= 0:
                    return False
                self.config['sync_interval'] = value

            elif option == 'log_level':
                if str(value).upper() not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                    return False
                self.config['log_level'] = str(value).upper()

            elif option == 'max_log_size':
                value = float(value)
                if value <= 0:
                    return False
                self.config['max_log_size'] = value

            return self.save_config()
        except (ValueError, TypeError):
            return False

    def get_config(self) -> Dict[str, Union[int, str, float]]:
        return {
            'sync_interval': self.config.get('sync_interval', 60),
            'log_level': self.config.get('log_level', 'INFO'),
            'max_log_size': self.config.get('max_log_size', 10)
        }

    def get_log_dir(self) -> Path:
        return self._log_dir

    def get_log_file(self) -> Path:
        log_dir = self.get_log_dir()
        current_date = datetime.now().strftime("%Y-%m-%d")
        return log_dir / f"folder_replicator_{current_date}.log"
