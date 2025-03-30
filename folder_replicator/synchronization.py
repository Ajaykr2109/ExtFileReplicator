import os
import time
import logging
import shutil
from .file_operations import FileOperations

logger = logging.getLogger("FolderReplicator")


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

            logger.info(f"Starting synchronization: {source} -> {destination}")
            start_time = time.time()
            stats = {'copied': 0, 'skipped': 0, 'removed': 0, 'errors': 0}

            if not FileOperations.ensure_directory_exists(destination):
                logger.error(
                    f"Failed to create destination directory: {destination}")
                return False

            for root, dirs, files in os.walk(source):
                dirs[:] = [d for d in dirs if not self._is_excluded(
                    os.path.join(root, d), exclusions)]
                rel_path = os.path.relpath(root, source)
                dest_dir = os.path.join(destination, rel_path)
                if not FileOperations.ensure_directory_exists(dest_dir):
                    stats['errors'] += 1
                    logger.warning(f"Failed to create directory: {dest_dir}")
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
                        logger.info(f"Copied: {src_file} -> {dest_file}")
                    else:
                        stats['errors'] += 1
                        logger.warning(f"Failed to copy: {src_file}")

            del_stats = self._cleanup_deleted_items(
                source, destination, exclusions)
            if del_stats:
                stats['removed'] += del_stats.get('removed', 0)
                stats['errors'] += del_stats.get('errors', 0)

            self.config_manager.update_last_sync(
                self.config_manager.get_replications().index(replication),
                time.time()
            )

            elapsed = time.time() - start_time
            logger.info("Synchronization statistics: " +
                        f"Copied: {stats['copied']}, " +
                        f"Skipped: {stats['skipped']}, " +
                        f"Removed: {stats['removed']}, " +
                        f"Errors: {stats['errors']}, " +
                        f"Time: {elapsed:.2f}s")
            return True

        except Exception as e:
            logger.error(
                f"Error during synchronization: {str(e)}", exc_info=True)
            return False

    def _is_excluded(self, path, exclusions):
        """Check if path matches any exclusion pattern"""
        path = path.replace('\\', '/')
        return any(excl in path for excl in exclusions)

    def _cleanup_deleted_items(self, source, destination, exclusions):
        stats = {'removed': 0, 'errors': 0}
        try:
            if not os.path.exists(destination):
                return stats

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
                            stats['removed'] += 1
                            logger.info(
                                f"Removed: {dest_file} (source deleted)")
                        except Exception as e:
                            stats['errors'] += 1
                            logger.error(
                                f"Error removing file {dest_file}: {e}")

                for dir in dirs:
                    dest_dir_path = os.path.join(root, dir)
                    src_dir_path = os.path.join(src_dir, dir)

                    if not os.path.exists(src_dir_path):
                        try:
                            shutil.rmtree(dest_dir_path)
                            stats['removed'] += 1
                            logger.info(
                                f"Removed directory: {dest_dir_path} (source deleted)")
                        except Exception as e:
                            stats['errors'] += 1
                            logger.error(
                                f"Error removing directory {dest_dir_path}: {e}")
        except Exception as e:
            stats['errors'] += 1
            logger.error(f"Error during cleanup: {e}")
        return stats

    def check_status(self, replication):
        """Check status of a replication"""
        source = replication['source']
        destination = replication['destination']

        if not os.path.exists(source):
            return {'error': 'Source path does not exist'}

        if not os.path.exists(destination):
            return {'error': 'Destination path does not exist'}

        # Count files in source
        source_files = set()
        for root, _, files in os.walk(source):
            for file in files:
                source_files.add(os.path.join(root, file))

        # Count files in destination
        dest_files = set()
        for root, _, files in os.walk(destination):
            for file in files:
                dest_files.add(os.path.join(root, file))

        return {
            'last_sync': replication.get('last_sync', 'Never'),
            'files_synced': len(dest_files),
            'pending_changes': len(source_files - dest_files)
        }

    def check_status(self, replication):
        """Check the sync status of a replication pair"""
        source = replication['source']
        destination = replication['destination']
        stats = {
            'last_sync': replication.get('last_sync', 'Never'),
            'source_files': 0,
            'dest_files': 0,
            'pending_changes': 0,
            'errors': 0
        }

        try:
            # Count source files
            if os.path.exists(source):
                for root, _, files in os.walk(source):
                    stats['source_files'] += len(files)

            # Count destination files
            if os.path.exists(destination):
                for root, _, files in os.walk(destination):
                    stats['dest_files'] += len(files)

            # Calculate pending changes
            stats['pending_changes'] = max(
                0, stats['source_files'] - stats['dest_files'])

        except Exception as e:
            stats['errors'] += 1
            logger.error(f"Error checking status: {str(e)}")

        return stats
