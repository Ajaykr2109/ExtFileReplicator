import os
import time
import shutil
from folder_replicator.file_operations import FileOperations


class Synchronizer:
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def sync_all(self):
        """Sync all configured replications"""
        for replication in self.config_manager.get_replications():
            self.sync_replication(replication)

    def sync_replication(self, replication):
        """Synchronize source to destination"""
        try:
            source = replication['source']
            destination = replication['destination']
            exclusions = replication.get('exclusions', [])

            print(f"\nStarting synchronization: {source} → {destination}")
            start_time = time.time()

            # Create destination root if needed
            if not FileOperations.ensure_directory_exists(destination):
                return False

            # Walk through source directory
            for root, dirs, files in os.walk(source):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self._is_excluded(
                    os.path.join(root, d), exclusions)]

                # Calculate relative path and destination path
                rel_path = os.path.relpath(root, source)
                dest_dir = os.path.join(destination, rel_path)

                # Create destination directory if it doesn't exist
                if not FileOperations.ensure_directory_exists(dest_dir):
                    continue

                # Process files
                for file in files:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)

                    # Skip excluded files
                    if self._is_excluded(src_file, exclusions):
                        continue

                    # Skip if destination file exists and is identical
                    if os.path.exists(dest_file):
                        if FileOperations.files_identical(src_file, dest_file):
                            continue

                    # Copy the file
                    if FileOperations.safe_copy(src_file, dest_file):
                        print(f"Copied: {src_file} → {dest_file}")

            # Handle directory deletions (optional)
            self._cleanup_deleted_items(source, destination, exclusions)

            # Update last sync time
            self.config_manager.update_last_sync(
                self.config_manager.get_replications().index(replication),
                time.time()
            )

            elapsed = time.time() - start_time
            print(f"Synchronization completed in {elapsed:.2f} seconds")
            return True

        except Exception as e:
            print(f"Error during synchronization: {e}")
            return False

    def _is_excluded(self, path, exclusions):
        """Check if path matches any exclusion pattern"""
        path = path.replace('\\', '/')  # Normalize path
        return any(excl in path for excl in exclusions)

    def _cleanup_deleted_items(self, source, destination, exclusions):
        """Remove files/directories in destination that don't exist in source"""
        try:
            for root, dirs, files in os.walk(destination):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not self._is_excluded(
                    os.path.join(root, d), exclusions)]

                rel_path = os.path.relpath(root, destination)
                src_dir = os.path.join(source, rel_path)

                # Check files
                for file in files:
                    dest_file = os.path.join(root, file)
                    src_file = os.path.join(src_dir, file)

                    if self._is_excluded(dest_file, exclusions):
                        continue

                    if not os.path.exists(src_file):
                        try:
                            os.remove(dest_file)
                            print(f"Removed (source deleted): {dest_file}")
                        except Exception as e:
                            print(f"Error removing file {dest_file}: {e}")

                # Check directories
                for dir in dirs:
                    dest_dir_path = os.path.join(root, dir)
                    src_dir_path = os.path.join(src_dir, dir)

                    if not os.path.exists(src_dir_path):
                        try:
                            shutil.rmtree(dest_dir_path)
                            print(
                                f"Removed directory (source deleted): {dest_dir_path}")
                        except Exception as e:
                            print(
                                f"Error removing directory {dest_dir_path}: {e}")
        except Exception as e:
            print(f"Error during cleanup: {e}")
