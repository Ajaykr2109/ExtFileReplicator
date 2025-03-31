import json
import os
from pathlib import Path
from datetime import datetime
import platform


class ConfigManager:
    def __init__(self, config_file='replicator_config.json'):
        self.config_file = config_file
        self.config = self._load_config()
        self._log_dir = self._init_log_dir()

    def _init_log_dir(self):
        """Initialize and return the log directory path"""
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

    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        return {"replications": []}

    def save_config(self):
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def add_replication(self, source, destination, exclusions=None):
        """Add a new replication pair to configuration"""
        try:
            source = str(Path(source).resolve())
            destination = str(Path(destination).resolve())

            if not os.path.exists(source):
                raise FileNotFoundError(
                    f"Source folder does not exist: {source}")

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

    def get_replications(self):
        """Get all configured replications"""
        return self.config.get('replications', [])

    def update_last_sync(self, replication_index, timestamp):
        """Update last sync time for a replication"""
        try:
            if 0 <= replication_index < len(self.config['replications']):
                self.config['replications'][replication_index]['last_sync'] = timestamp
                return self.save_config()
            return False
        except Exception as e:
            print(f"Error updating last sync: {e}")
            return False

    def remove_replication(self, source_path):
        """Remove a replication pair by source path"""
        self.config['replications'] = [r for r in self.config['replications']
                                       if r['source'] != source_path]
        return self.save_config()

    def get_log_file(self):
        """Get path to current log file"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        return self._log_dir / f"folder_replicator_{current_date}.log"

    def set_config(self, option, value):
        """Set a configuration value"""
        if option == 'log_level':
            value = value.upper()
        self.config[option] = value
        return self.save_config()

    def get_config(self):
        """Get current configuration"""
        return {
            'sync_interval': self.config.get('sync_interval', 60),
            'log_level': self.config.get('log_level', 'INFO'),
            'max_log_size': self.config.get('max_log_size', 10)
        }

    def get_log_dir(self):
        """Get the log directory path"""
        return self._log_dir

    def get_log_file(self):
        """Get path to current log file"""
        log_dir = self.get_log_dir()
        current_date = datetime.now().strftime("%Y-%m-%d")
        return log_dir / f"folder_replicator_{current_date}.log"

    def set_config(self, option, value):
        """Set a configuration value"""
        if not hasattr(self, 'config'):
            self.config = {}

        if option == 'sync_interval':
            try:
                value = int(value)
                if value <= 0:
                    return False
            except ValueError:
                return False

        elif option == 'log_level':
            if value.upper() not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                return False
            value = value.upper()

        elif option == 'max_log_size':
            try:
                value = float(value)
                if value <= 0:
                    return False
            except ValueError:
                return False

        self.config[option] = value
        return self.save_config()

    def get_config(self):
        """Get current configuration"""
        return {
            'sync_interval': self.config.get('sync_interval', 60),
            'log_level': self.config.get('log_level', 'INFO'),
            'max_log_size': self.config.get('max_log_size', 10)
        }
