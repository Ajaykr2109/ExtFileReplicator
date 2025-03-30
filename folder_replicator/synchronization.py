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
        """Synchronize source to destination with statistics"""
        try:
            source = replication['source']
            destination = replication['destination']
            exclusions = replication.get('exclusions', [])

            print(f"\nStarting synchronization: {source} → {destination}")
            start_time = time.time()
            stats = {'copied': 0, 'skipped': 0, 'removed': 0, 'errors': 0}

            if not FileOperations.ensure_directory_exists(destination):
                return False

            for root, dirs, files in os.walk(source):

                dirs[:] = [d for d in dirs if not self._is_excluded(
                    os.path.join(root, d), exclusions)]

                rel_path = os.path.relpath(root, source)
                dest_dir = os.path.join(destination, rel_path)

                if not FileOperations.ensure_directory_exists(dest_dir):
                    stats['errors'] += 1
                    continue

                for file in files:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)

                    if self._is_excluded(src_file, exclusions):
                        stats['skipped'] += 1
                        continue

                    if os.path.exists(dest_file):
                        if FileOperations.files_identical(src_file, dest_file):
                            stats['skipped'] += 1
                            continue

                    if FileOperations.safe_copy(src_file, dest_file):
                        stats['copied'] += 1
                        print(f"Copied: {src_file} → {dest_file}")
                    else:
                        stats['errors'] += 1

            del_stats = self._cleanup_deleted_items(
                source, destination, exclusions)
            stats['removed'] = del_stats.get('removed', 0)
            stats['errors'] += del_stats.get('errors', 0)

            self.config_manager.update_last_sync(
                self.config_manager.get_replications().index(replication),
                time.time()
            )

            elapsed = time.time() - start_time
            print("\nSynchronization statistics:")
            print(f"- Files copied: {stats['copied']}")
            print(f"- Files skipped (unchanged): {stats['skipped']}")
            print(f"- Files/directories removed: {stats['removed']}")
            print(f"- Errors encountered: {stats['errors']}")
            print(f"Completed in {elapsed:.2f} seconds")
            return True

        except Exception as e:
            print(f"Error during synchronization: {e}")
            return False

    def _cleanup_deleted_items(self, source, destination, exclusions):
        """Remove files/directories in destination that don't exist in source"""
        stats = {'removed': 0, 'errors': 0}
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
                            stats['removed'] += 1
                            print(f"Removed (source deleted): {dest_file}")
                        except Exception as e:
                            stats['errors'] += 1
                            print(f"Error removing file {dest_file}: {e}")

                # Check directories
                for dir in dirs:
                    dest_dir_path = os.path.join(root, dir)
                    src_dir_path = os.path.join(src_dir, dir)

                    if not os.path.exists(src_dir_path):
                        try:
                            shutil.rmtree(dest_dir_path)
                            stats['removed'] += 1
                            print(
                                f"Removed directory (source deleted): {dest_dir_path}")
                        except Exception as e:
                            stats['errors'] += 1
                            print(
                                f"Error removing directory {dest_dir_path}: {e}")
        except Exception as e:
            stats['errors'] += 1
            print(f"Error during cleanup: {e}")
        return stats

    def _is_excluded(self, path, exclusions):
        """Check if path matches any exclusion pattern"""
        path = path.replace('\\', '/')
        return any(excl in path for excl in exclusions)

    def _cleanup_deleted_items(self, source, destination, exclusions):
        """Remove files/directories in destination that don't exist in source"""
        try:
            for root, dirs, files in os.walk(destination):

                dirs[:] = [d for d in dirs if not self._is_excluded(
                    os.path.join(root, d), exclusions)]

                rel_path = os.path.relpath(root, destination)
                src_dir = os.path.join(source, rel_path)

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
