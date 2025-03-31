# Folder Replicator

A lightweight yet powerful folder synchronization tool with version control-like capabilities.

## Features

- 🔄 One-way folder synchronization (source → destination)
- 👁️ Real-time file monitoring with automatic updates
- ⚡ Fast change detection using file hashing
- 📁 Handles all file types (binary, text, hidden files)
- ⏱️ Preserves file timestamps and metadata
- 🚫 Configurable file/folder exclusions
- 🖥️ Cross-platform (Windows/macOS/Linux)

## Installation

### Requirements

- Python 3.6+
- pip package manager

### Quick Install

```bash
pip install git+https://github.com/Ajaykr2109/ExtFileReplicator
```

### Development Install

```bash
git clone https://github.com/Ajaykr2109/ExtFileReplicator.git
cd ExtFileReplicator
pip install -e .
```

## Command Reference

### Basic Operations

| Command               | Description              | Example                          |
| --------------------- | ------------------------ | -------------------------------- |
| `add <source> <dest>` | Add new replication pair | `frep add ~/Docs ~/Backups/Docs` |
| `sync`                | Run one-time sync        | `frep sync`                      |
| `watch`               | Continuous monitoring    | `frep watch --interval 30`       |

### Advanced Operations

| Command                  | Description           | Example                            |
| ------------------------ | --------------------- | ---------------------------------- |
| `list`                   | List all replications | `frep list`                        |
| `remove <source>`        | Remove replication    | `frep remove ~/Docs`               |
| `status [source]`        | Check sync status     | `frep status ~/Docs`               |
| `logs [--tail N]`        | View logs             | `frep logs --tail 50`              |
| `logs --clear`           | Clear logs            | `frep logs --clear`                |
| `config set <opt> <val>` | Set configuration     | `frep config set sync_interval 60` |
| `config show`            | Show configuration    | `frep config show`                 |

### Common Flags

| Flag        | Description        |
| ----------- | ------------------ |
| `--verbose` | Detailed output    |
| `--quiet`   | Only show errors   |
| `--dry-run` | Simulation mode    |
| `--force`   | Skip confirmations |

## Usage Examples

1. **Basic Setup**

```bash
frep add ~/Documents ~/Backups/Documents --exclude *.tmp cache/
frep sync
```

2. **Continuous Monitoring**

```bash
frep watch --interval 60  # Syncs every hour
```

3. **Troubleshooting**

```bash
frep logs --tail 20  # Check recent logs
frep status ~/Documents  # Check sync status
```

## Configuration

- **Config File**: `replicator_config.json` in working directory
- **Log Locations**:
  - Windows: `%LOCALAPPDATA%\FolderReplicator\Logs\`
  - macOS: `~/Library/Logs/FolderReplicator/`
  - Linux: `~/.local/share/FolderReplicator/logs/`

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: File access error
- `4`: Configuration error

## License

MIT License

---
