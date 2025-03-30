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

    pip install git+https://github.com/yourusername/folder-replicator.git

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

## License

    MIT License. See LICENSE for details.
