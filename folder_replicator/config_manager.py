import json
import os
from pathlib import Path


class ConfigManager:
    def __init__(self, config_file='replicator_config.json'):
        self.config_file = config_file
        self.config = self._load_config()

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
