# -*- coding: utf-8 -*-
import os
import site
import sys
from setuptools import setup, find_packages


def read_file(filename):
    """Read a UTF-8 encoded text file and return its contents."""
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


# Get the long description from README.md
try:
    long_description = read_file("README.md")
except (IOError, FileNotFoundError):
    long_description = "A CLI-based folder replication and synchronization tool."

# Detect if we're in a virtual environment
in_venv = sys.prefix != sys.base_prefix
user_site = site.USER_SITE

setup(
    name="ext_folder_replicator",
    version="1.0.0",
    author="ajaykr2109_nowStack",
    author_email="chaturvedikraj2109@gmail.com",
    description="A CLI-based folder replication and synchronization tool.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ajaykr2109/ExtFileReplicator",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "watchdog>=2.1.0",
        "daemon>=1.2",
        "lockfile>=0.12.2",
    ],
    extras_require={
        "windows": ["pywin32>=300; sys_platform == 'win32'"]
    },
    entry_points={
        "console_scripts": [
            "frep=folder_replicator.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Filesystems",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
    options={
        'install': {
            'install_lib': 'lib/python' if not in_venv and user_site else None,
            'user': not in_venv
        }
    }
)
