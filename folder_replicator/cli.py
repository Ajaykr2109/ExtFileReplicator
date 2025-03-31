import argparse
import sys
from pathlib import Path
import platform
from .config_manager import ConfigManager
from .synchronization import Synchronizer
from .watcher import ReplicationWatcher
from .logger import setup_logger
from .service_manager import ServiceManager


def main():
    config_manager = ConfigManager()
    logger = setup_logger(config_manager)
    parser = argparse.ArgumentParser(description='Folder Replication Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Common arguments
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        '--verbose', action='store_true', help='Verbose output')
    common_parser.add_argument(
        '--quiet', action='store_true', help='Only show errors')
    common_parser.add_argument(
        '--dry-run', action='store_true', help='Simulation mode')
    common_parser.add_argument(
        '--force', action='store_true', help='Skip confirmations')
    common_parser.add_argument('--daemon', action='store_true',
                               help='Run as background service')

    # Add command
    add_parser = subparsers.add_parser(
        'add', parents=[common_parser], help='Add a new replication pair')
    add_parser.add_argument('source', help='Source directory path')
    add_parser.add_argument('destination', help='Destination directory path')
    add_parser.add_argument('--exclude', nargs='*',
                            default=[], help='File patterns to exclude')

    # Sync command
    sync_parser = subparsers.add_parser(
        'sync', parents=[common_parser], help='Run synchronization')

    # Watch command - MODIFIED to support service mode
    watch_parser = subparsers.add_parser(
        'watch', parents=[common_parser], help='Continuous monitoring mode')
    watch_parser.add_argument('--interval', type=int,
                              default=5, help='Sync interval in minutes')

    # List command
    subparsers.add_parser(
        'list', parents=[common_parser], help='List all replications')

    # Remove command
    remove_parser = subparsers.add_parser(
        'remove', parents=[common_parser], help='Remove a replication')
    remove_parser.add_argument('source_path', help='Source path to remove')

    # Status command
    status_parser = subparsers.add_parser(
        'status', parents=[common_parser], help='Check replication status')
    status_parser.add_argument(
        'source_path', nargs='?', help='Specific source to check')

    # Logs command
    logs_parser = subparsers.add_parser(
        'logs', parents=[common_parser], help='View logs')
    logs_parser.add_argument('--tail', type=int, help='Show last N lines')
    logs_parser.add_argument(
        '--clear', action='store_true', help='Clear log file')

    # Config command
    config_parser = subparsers.add_parser(
        'config', parents=[common_parser], help='Configuration management')
    config_subparsers = config_parser.add_subparsers(
        dest='config_command', required=True)

    config_set = config_subparsers.add_parser(
        'set', parents=[common_parser], help='Set configuration value')
    config_set.add_argument(
        'option', help='Option to set (sync_interval/log_level/max_log_size)')
    config_set.add_argument('value', help='Value to set')

    config_subparsers.add_parser(
        'show', parents=[common_parser], help='Show current configuration')

    # NEW: Service command for Windows
    if platform.system() == 'Windows':
        service_parser = subparsers.add_parser(
            'service', help='Windows service management')
        service_parser.add_argument('action', choices=['install', 'start', 'stop', 'restart'],
                                    help='Service action to perform')

    args = parser.parse_args()

    config = ConfigManager()
    sync = Synchronizer(config)

    try:
        if args.command == 'add':
            logger.info(
                f"Adding replication: {args.source} -> {args.destination}")
            if config.add_replication(args.source, args.destination, args.exclude):
                logger.info("Successfully added replication")
                if not args.dry_run:
                    sync.sync_replication(config.get_replications()[-1])
            else:
                logger.error("Failed to add replication")

        elif args.command == 'sync':
            logger.info("Starting synchronization")
            if not args.dry_run:
                sync.sync_all()

        elif args.command == 'watch':
            logger.info(
                f"Starting watch mode (interval: {args.interval} minutes)")
            if not args.dry_run:
                if args.daemon:
                    service = ServiceManager(args.interval)
                    if platform.system() == 'Windows' and hasattr(args, 'action'):
                        # Handle Windows service commands
                        if args.action == 'install':
                            logger.info("Installing Windows service...")
                        service.run_as_service()
                    else:
                        service.run_as_service()
                else:
                    watcher = ReplicationWatcher(sync, args.interval)
                    watcher.watch()

        elif args.command == 'list':
            for rep in config.get_replications():
                print(f"{rep['source']} -> {rep['destination']}")

        elif args.command == 'remove':
            if args.force or input(f"Remove {args.source_path}? [y/N] ").lower() == 'y':
                if config.remove_replication(args.source_path):
                    logger.info("Replication removed")
                else:
                    logger.error("Replication not found")

        elif args.command == 'status':
            replications = config.get_replications()

            if args.source_path:

                rep = next(
                    (r for r in replications if r['source'] == args.source_path), None)
                if not rep:
                    logger.error(
                        f"No replication found for: {args.source_path}")
                    return 1

                status = sync.check_status(rep)
                print(f"\nStatus for {rep['source']} -> {rep['destination']}:")
                print(f"Last sync: {status.get('last_sync', 'Never')}")
                print(f"Source files: {status.get('source_files', 0)}")
                print(f"Destination files: {status.get('dest_files', 0)}")
                print(f"Pending changes: {status.get('pending_changes', 0)}")
                if status.get('errors'):
                    print(f"Errors: {status.get('errors', 0)}")
            else:

                if not replications:
                    print("No replications configured")
                    return

                print("\nReplication Status Summary:")
                for rep in replications:
                    status = sync.check_status(rep)
                    print(f"\n{rep['source']} -> {rep['destination']}")
                    print(f"  Last sync: {status.get('last_sync', 'Never')}")
                    print(
                        f"  Files synced: {status.get('dest_files', 0)}/{status.get('source_files', 0)}")
                    print(
                        f"  Pending changes: {status.get('pending_changes', 0)}")
                    if status.get('errors'):
                        print(f"  Errors: {status.get('errors', 0)}")

        elif args.command == 'logs':
            log_file = config.get_log_file()

            if args.clear:
                if args.force or input("Clear all logs? [y/N] ").lower() == 'y':
                    try:
                        with open(log_file, 'w'):
                            pass
                        logger.info("Logs cleared successfully")
                    except Exception as e:
                        logger.error(f"Failed to clear logs: {str(e)}")

            elif args.tail:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if args.tail > len(lines):
                            print(f"Only {len(lines)} lines available:")
                        print(''.join(lines[-args.tail:]))
                except FileNotFoundError:
                    logger.error("Log file not found")
                except Exception as e:
                    logger.error(f"Error reading logs: {str(e)}")

            else:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        print(f.read())
                except FileNotFoundError:
                    logger.error("Log file not found")
                except Exception as e:
                    logger.error(f"Error reading logs: {str(e)}")

        elif args.command == 'config':
            if args.config_command == 'set':
                valid_options = ['sync_interval', 'log_level', 'max_log_size']
                if args.option not in valid_options:
                    logger.error(
                        f"Invalid option. Must be one of: {', '.join(valid_options)}")
                    return 1

                if args.option == 'log_level' and args.value.upper() not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                    logger.error(
                        "Invalid log level. Must be DEBUG/INFO/WARNING/ERROR")
                    return 1

                if args.option == 'sync_interval':
                    try:
                        args.value = int(args.value)
                        if args.value <= 0:
                            raise ValueError
                    except ValueError:
                        logger.error(
                            "Sync interval must be a positive integer (minutes)")
                        return 1

                if args.option == 'max_log_size':
                    try:
                        args.value = float(args.value)
                        if args.value <= 0:
                            raise ValueError
                    except ValueError:
                        logger.error(
                            "Max log size must be a positive number (MB)")
                        return 1

                if config_manager.set_config(args.option, args.value):
                    logger.info(
                        f"Configuration updated: {args.option} = {args.value}")
                else:
                    logger.error("Failed to update configuration")

            elif args.config_command == 'show':
                config = config_manager.get_config()
                print("\nCurrent Configuration:")
                print(
                    f"Sync interval: {config.get('sync_interval', 60)} minutes")
                print(f"Log level: {config.get('log_level', 'INFO')}")
                print(f"Max log size: {config.get('max_log_size', 10)} MB")

                print(f"Log directory: {config_manager.get_log_dir()}")

        elif args.command == 'logs':
            log_file = config_manager.get_log_file()

            if args.clear:
                if args.force or input("Clear all logs? [y/N] ").lower() == 'y':
                    try:
                        with open(log_file, 'w'):
                            pass
                        logger.info("Logs cleared successfully")
                    except Exception as e:
                        logger.error(f"Failed to clear logs: {str(e)}")

            elif args.tail:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if args.tail > len(lines):
                            print(f"Only {len(lines)} lines available:")
                        print(''.join(lines[-args.tail:]))
                except FileNotFoundError:
                    logger.error("Log file not found")
                except Exception as e:
                    logger.error(f"Error reading logs: {str(e)}")

            else:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        print(f.read())
                except FileNotFoundError:
                    logger.error("Log file not found")
                except Exception as e:
                    logger.error(f"Error reading logs: {str(e)}")

        elif args.command == 'service' and platform.system() == 'Windows':
            service = ServiceManager()
            if args.action == 'install':
                logger.info("Installing Windows service...")
            elif args.action == 'start':
                service.run_as_service()
            elif args.action == 'stop':
                service.stop()
            elif args.action == 'restart':
                service.stop()
                service.run_as_service()
    except Exception as e:
        if logger:
            logger.error(f"Error: {str(e)}", exc_info=True)
        else:
            print(f"Critical error before logger setup: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
