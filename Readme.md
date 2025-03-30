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

# Folder Replicator CLI Commands (Latest Version)

Here are all the available command-line interface commands for your Folder Replicator application:

## Basic Commands

### 1. Add a new replication pair

```bash
folder-replicate add <source_path> <destination_path> [--exclude PATTERNS]
```

Example:

```bash
folder-replicate add C:\Users\Me\Documents D:\Backups\Documents --exclude *.tmp temp/
```

### 2. Run a one-time synchronization

```bash
folder-replicate sync
```

- Synchronizes all configured replication pairs
- Shows detailed statistics of operations

### 3. Start continuous watching with periodic sync

```bash
folder-replicate watch [--interval MINUTES]
```

Example (sync every 30 minutes):

```bash
folder-replicate watch --interval 30
```

## Advanced Commands

### 4. List all configured replications

```bash
folder-replicate list
```

- Shows all source-destination pairs
- Displays last sync time for each

### 5. Remove a replication

```bash
folder-replicate remove <source_path>
```

Example:

```bash
folder-replicate remove C:\Users\Me\Documents
```

### 6. Check replication status

```bash
folder-replicate status [source_path]
```

Example (check all):

```bash
folder-replicate status
```

Example (check specific):

```bash
folder-replicate status C:\Users\Me\Documents
```

### 7. View logs

```bash
folder-replicate logs [--tail LINES] [--clear]
```

Examples:

```bash
folder-replicate logs              # Show complete log
folder-replicate logs --tail 50    # Show last 50 lines
folder-replicate logs --clear      # Clear log file
```

## Configuration Commands

### 8. Set global options

```bash
folder-replicate config set <option> <value>
```

Available options:

- `sync_interval` (minutes)
- `log_level` (DEBUG, INFO, WARNING, ERROR)
- `max_log_size` (in MB)

Example:

```bash
folder-replicate config set sync_interval 60
```

### 9. Show current configuration

```bash
folder-replicate config show
```

## Help Command

### 10. Display help

```bash
folder-replicate --help
folder-replicate <command> --help
```

## Special Flags (Available for Most Commands)

- `--verbose` - Show detailed output
- `--quiet` - Only show errors
- `--dry-run` - Simulate operations without making changes
- `--force` - Skip confirmation prompts

Example with flags:

```bash
folder-replicate sync --verbose --dry-run
```

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
