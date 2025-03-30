import argparse
from .config_manager import ConfigManager
from .synchronization import Synchronizer
from .watcher import ReplicationWatcher
from .logger import setup_logger

logger = setup_logger()


def main():
    parser = argparse.ArgumentParser(description="Folder Replication Tool")
    subparsers = parser.add_subparsers(dest='command', required=True)

    add_parser = subparsers.add_parser('add', help='Add a new replication')
    add_parser.add_argument('source', help='Source directory path')
    add_parser.add_argument('destination', help='Destination directory path')
    add_parser.add_argument('--exclude', nargs='*', default=[],
                            help='Patterns to exclude from sync')

    sync_parser = subparsers.add_parser('sync', help='Run synchronization')

    watch_parser = subparsers.add_parser(
        'watch', help='Watch for changes and auto-sync')
    watch_parser.add_argument('--interval', type=int, default=60,
                              help='Periodic sync interval in minutes (default: 60)')

    args = parser.parse_args()

    logger.info("Starting Folder Replicator")
    config_manager = ConfigManager()
    synchronizer = Synchronizer(config_manager)

    if args.command == 'add':
        logger.info(
            f"Adding new replication: {args.source} → {args.destination}")
        success = config_manager.add_replication(
            args.source, args.destination, args.exclude)
        if success:
            logger.info("Replication added successfully")
            synchronizer.sync_replication(
                config_manager.get_replications()[-1])
        else:
            logger.error("Failed to add replication")

    elif args.command == 'sync':
        logger.info("Starting synchronization for all replications")
        synchronizer.sync_all()

    elif args.command == 'watch':
        logger.info(
            f"Starting watch mode with {args.interval} minute sync interval")
        watcher = ReplicationWatcher(synchronizer, args.interval)
        watcher.watch()
