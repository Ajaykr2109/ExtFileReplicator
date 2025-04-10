## Command Reference

### Basic Operations

| Command                    | Description                 | Example                                          |
| -------------------------- | --------------------------- | ------------------------------------------------ |
| `add <source> <dest>`      | Add new replication pair    | `frep add ~/Docs ~/Backups/Docs`                 |
| `add --exclude <patterns>` | Add with exclusion patterns | `frep add ~/Docs ~/Backup --exclude *.tmp *.log` |
| `sync`                     | Run one-time sync           | `frep sync`                                      |
| `watch`                    | Start continuous monitoring | `frep watch`                                     |

### Watch Mode Options

| Command                   | Description                  | Example                      |
| ------------------------- | ---------------------------- | ---------------------------- |
| `watch --interval <mins>` | Set sync interval in minutes | `frep watch --interval 30`   |
| `watch --daemon` or `-d`  | Run in background mode       | `frep watch --interval 5 -d` |

### Management Commands

| Command           | Description                  | Example              |
| ----------------- | ---------------------------- | -------------------- |
| `list`            | List all replications        | `frep list`          |
| `remove <source>` | Remove a replication         | `frep remove ~/Docs` |
| `status`          | Show all replications status | `frep status`        |
| `status <source>` | Check specific replication   | `frep status ~/Docs` |

### Configuration Commands

| Command                          | Description                 | Example                            |
| -------------------------------- | --------------------------- | ---------------------------------- |
| `config show`                    | Display current settings    | `frep config show`                 |
| `config set sync_interval <val>` | Set sync interval (minutes) | `frep config set sync_interval 60` |
| `config set log_level <val>`     | Set log level               | `frep config set log_level DEBUG`  |
| `config set max_log_size <val>`  | Set max log size (MB)       | `frep config set max_log_size 10`  |

### Log Management

| Command           | Description             | Example               |
| ----------------- | ----------------------- | --------------------- |
| `logs`            | View complete logs      | `frep logs`           |
| `logs --tail <N>` | View last N log entries | `frep logs --tail 50` |
| `logs --clear`    | Clear all logs          | `frep logs --clear`   |

### Global Flags

These flags can be used with any command:

| Flag        | Description          | Example                       |
| ----------- | -------------------- | ----------------------------- |
| `--verbose` | Show detailed output | `frep sync --verbose`         |
| `--quiet`   | Show only errors     | `frep sync --quiet`           |
| `--dry-run` | Simulation mode      | `frep add src dest --dry-run` |
| `--force`   | Skip confirmations   | `frep remove src --force`     |

## Configuration Options

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General operational information
- `WARNING`: Warning messages
- `ERROR`: Error conditions only

### File Patterns for Exclusion

- Supports glob patterns: `*.tmp`, `*.log`, `cache/`
- Multiple patterns: `--exclude *.tmp *.bak cache/`

## Usage Examples

1. **Basic Setup**

```bash
# Add a new replication with exclusions
frep add ~/Documents ~/Backups/Documents --exclude *.tmp cache/
# Run initial sync
frep sync
```

2. **Background Monitoring**

```bash
# Start monitoring in background with 5-minute interval
frep watch --interval 5 --daemon
# Check status
frep status
```

3. **Advanced Configuration**

```bash
# Set debug logging
frep config set log_level DEBUG
# Set 30-minute sync interval
frep config set sync_interval 30
# Set 20MB max log size
frep config set max_log_size 20
```

4. **Maintenance**

```bash
# View recent logs
frep logs --tail 20
# Remove a replication without confirmation
frep remove ~/Documents --force
# Check specific replication status
frep status ~/Projects
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
