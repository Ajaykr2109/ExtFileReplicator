import argparse
from folder_replicator.config_manager import ConfigManager
from folder_replicator.synchronization import Synchronizer
from folder_replicator.watcher import ReplicationWatcher


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

    config_manager = ConfigManager()
    synchronizer = Synchronizer(config_manager)

    if args.command == 'add':
        success = config_manager.add_replication(
            args.source, args.destination, args.exclude)
        if success:
            print(f"Added replication: {args.source} → {args.destination}")
            synchronizer.sync_replication(
                config_manager.get_replications()[-1])
        else:
            print("Failed to add replication")

    elif args.command == 'sync':
        print("Starting synchronization for all replications...")
        synchronizer.sync_all()

    elif args.command == 'watch':
        print(
            f"Starting watch mode with periodic sync every {args.interval} minutes...")
        watcher = ReplicationWatcher(synchronizer, args.interval)
        watcher.watch()
