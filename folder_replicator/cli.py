import argparse
import sys
import logging
from pathlib import Path
import importlib.metadata
from folder_replicator.config_manager import ConfigManager
from folder_replicator.synchronization import Synchronizer
from folder_replicator.watcher import ReplicationWatcher
from folder_replicator.logger import setup_logger
from folder_replicator.gui import run_gui


def main():
    config_manager = ConfigManager()
    watcher = None  # Store watcher instance at module level

    parser = argparse.ArgumentParser(description='Folder Replication Tool')
    parser.add_argument('--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('--quiet', action='store_true',
                        help='Only show errors')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulation mode')
    parser.add_argument('--force', action='store_true',
                        help='Skip confirmations')
    parser.add_argument('-v', '--version',
                        action='store_true', help='Show version')

    subparsers = parser.add_subparsers(dest='command', required=False)

    # GUI command
    gui_parser = subparsers.add_parser('gui', help='Launch GUI interface')

    # Add command
    add_parser = subparsers.add_parser(
        'add', help='Add a new replication pair')
    add_parser.add_argument('source', help='Source directory path')
    add_parser.add_argument('destination', help='Destination directory path')
    add_parser.add_argument('--exclude', nargs='*', default=[],
                            help='File patterns to exclude (e.g., *.tmp cache/ *.pyc)')

    sync_parser = subparsers.add_parser('sync', help='Run synchronization')
    sync_parser.add_argument('source_path', nargs='?',
                             help='Specific source path to sync')

    watch_parser = subparsers.add_parser(
        'watch', help='Continuous monitoring mode')
    watch_parser.add_argument('--interval', type=int,
                              default=60, help='Sync interval in minutes')
    watch_parser.add_argument('--daemon', '-d', action='store_true',
                              help='Run watch mode as a background process')

    subparsers.add_parser('list', help='List all replications')

    remove_parser = subparsers.add_parser(
        'remove', help='Remove a replication')
    remove_parser.add_argument('source_path', help='Source path to remove')

    status_parser = subparsers.add_parser(
        'status', help='Check replication status')
    status_parser.add_argument(
        'source_path', nargs='?', help='Specific source to check')

    logs_parser = subparsers.add_parser('logs', help='View logs')
    logs_parser.add_argument('--tail', type=int, help='Show last N lines')
    logs_parser.add_argument(
        '--clear', action='store_true', help='Clear log file')

    config_parser = subparsers.add_parser(
        'config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(
        dest='config_command', required=True)

    config_set = config_subparsers.add_parser(
        'set', help='Set configuration value')
    config_set.add_argument(
        'option', help='Option to set (sync_interval/log_level/max_log_size)')
    config_set.add_argument('value', help='Value to set')

    config_subparsers.add_parser(
        'show', help='Show current configuration')

    for p in [add_parser, sync_parser, watch_parser, remove_parser, status_parser, logs_parser, config_set]:
        p.add_argument('--verbose', action='store_true', help='Verbose output')
        p.add_argument('--quiet', action='store_true', help='Only show errors')
        p.add_argument('--dry-run', action='store_true',
                       help='Simulation mode')
        p.add_argument('--force', action='store_true',
                       help='Skip confirmations')

    try:
        if len(sys.argv) == 1:
            return run_gui()  # Default to GUI when no arguments

        if len(sys.argv) == 2 and (sys.argv[1] == '-v' or sys.argv[1] == '--version'):
            try:
                version = importlib.metadata.version('ext_folder_replicator')
                print(f"ext_folder_replicator version {version}")
                return 0
            except importlib.metadata.PackageNotFoundError:
                print("Version information not available")
                return 1

        args = parser.parse_args()

        # Launch GUI if requested
        if args.command == 'gui' or not args.command:
            try:
                return run_gui()
            except ImportError as e:
                print(
                    "Error: GUI dependencies not installed. Please install with: pip install PyQt6 QDarkStyle")
                return 1
            except Exception as e:
                print(f"Error launching GUI: {str(e)}")
                return 1

        logger = setup_logger(
            config_manager, quiet=args.quiet, verbose=args.verbose)
        config = ConfigManager()
        sync = Synchronizer(config)

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
                if args.source_path:
                    # Sync specific replication
                    replications = [r for r in config.get_replications()
                                    if r['source'] == args.source_path]
                    if not replications:
                        logger.error(
                            f"No replication found for source: {args.source_path}")
                        return 1
                    sync.sync_replication(replications[0])
                else:
                    # Sync all replications
                    sync.sync_all()

        elif args.command == 'watch':
            logger.info(
                f"Starting watch mode (interval: {args.interval} minutes)")
            if args.daemon:
                import subprocess
                logger.info("Running watch mode in the background")
                subprocess.Popen([sys.executable, __file__, 'watch', '--interval', str(args.interval)],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                if not args.dry_run:
                    watcher = ReplicationWatcher(sync, args.interval)
                    try:
                        watcher.watch()
                    except KeyboardInterrupt:
                        logger.info(
                            "Received interrupt signal, stopping gracefully...")
                    finally:
                        if watcher:
                            watcher.stop()
                            watcher.cleanup()

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
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping gracefully...")
        if watcher:
            watcher.stop()
            watcher.cleanup()
    except Exception as e:
        if logger:
            logger.error(f"Error: {str(e)}", exc_info=True)
        else:
            print(f"Critical error before logger setup: {str(e)}")
        return 1
    finally:
        if watcher:
            watcher.stop()
            watcher.cleanup()


if __name__ == '__main__':
    sys.exit(main())
