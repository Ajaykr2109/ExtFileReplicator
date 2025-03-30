# Folder Replicator

A powerful folder synchronization tool with version control-like capabilities, built in Python.

## Features

    One-way folder synchronization (source → destination)

    Real-time file monitoring with automatic updates

    Fast change detection using file hashing

    Handles all file types (binary, text, hidden files)

    Preserves file timestamps and metadata

    Configurable file/folder exclusions

    Lightweight and cross-platform

## Installation

    Prerequisites
    Python 3.6+
    pip package manager

## Quick Install

    pip install git+https://github.com/Ajaykr2109/ExtFileReplicator

## Development Install

    Copy
    git clone https://github.com/yourusername/folder-replicator.git
    cd folder-replicator
    pip install -e .

## Usage

    Basic Commands
    folder-replicate add /path/to/source /path/to/destination - Add new replication pair
    folder-replicate sync - Run one-time synchronization
    folder-replicate watch - Start continuous monitoring

## Advanced Options

    folder-replicate add /source /dest --exclude *.tmp temp/ - Add with exclusions
    folder-replicate --help - View all commands

## Example Workflow

    folder-replicate add ~/Documents ~/Backups/Documents_backup

    folder-replicate sync

    folder-replicate watch (Press Ctrl+C to stop)

## Configuration

    Settings are stored in replicator_config.json in your working directory. You can:

    Manually edit this file when the tool isn't running

    View current replications

    Modify exclusion patterns

## Contributing

    Fork the repository

    Create a feature branch

    Commit your changes

    Push to the branch

    Open a Pull Request

## Logging

### Platform-specific log locations:

        Windows: %LOCALAPPDATA%\FolderReplicator\Logs

        macOS: ~/Library/Logs/FolderReplicator

        Linux: ~/.local/share/FolderReplicator/logs

    ### Daily log files:

        Creates new log files each day with names like folder_replicator_2023-11-15.log

        Comprehensive logging:

        Both file and console output

        Timestamps in log files

        Different log levels (INFO, WARNING, ERROR)

## License

    MIT License. See LICENSE for details.

--
#Commands

## Folder Replicator CLI Commands (Latest Version)

Here's the breakdown of all commands and their variations in your `cli.py` file:

### Main Commands (8 total):

1. **add** - Add a new replication pair

   - `frep add <source> <destination> [--exclude PATTERNS]`
   - With flags: `--verbose`, `--quiet`, `--dry-run`, `--force`

2. **sync** - Run synchronization

   - `frep sync`
   - With flags: `--verbose`, `--quiet`, `--dry-run`, `--force`

3. **watch** - Continuous monitoring mode

   - `frep watch [--interval MINUTES]`
   - With flags: `--verbose`, `--quiet`, `--dry-run`, `--force`

4. **list** - List all replications

   - `frep list`
   - With flags: `--verbose`, `--quiet`, `--dry-run`, `--force`

5. **remove** - Remove a replication

   - `frep remove <source_path>`
   - With flags: `--verbose`, `--quiet`, `--dry-run`, `--force`

6. **status** - Check replication status

   - `frep status` (all replications)
   - `frep status <source_path>` (specific replication)
   - With flags: `--verbose`, `--quiet`, `--dry-run`, `--force`

7. **logs** - View logs

   - `frep logs` (show full log)
   - `frep logs --tail N` (show last N lines)
   - `frep logs --clear` (clear log file)
   - With flags: `--verbose`, `--quiet`, `--dry-run`, `--force`

8. **config** - Configuration management
   - Subcommands:
     - `frep config set <option> <value>`
       - Options: `sync_interval`, `log_level`, `max_log_size`
     - `frep config show`
   - With flags: `--verbose`, `--quiet`, `--dry-run`, `--force`

### Global Flags (4 total):

Available for all commands:

1. `--verbose` - Show detailed output
2. `--quiet` - Only show errors
3. `--dry-run` - Simulation mode
4. `--force` - Skip confirmations

## Log File Location

Logs are automatically stored at:

- **Windows**: `%LOCALAPPDATA%\FolderReplicator\Logs\`
- **macOS**: `~/Library/Logs/FolderReplicator/`
- **Linux**: `~/.local/share/FolderReplicator/logs/`

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - File/folder access error
- `4` - Configuration error

You can check the exit code in scripts using:

```bash
echo $?  # On Linux/macOS
echo %ERRORLEVEL%  # On Windows
```
