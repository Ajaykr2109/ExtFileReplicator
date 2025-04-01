# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import io
import os


def read_file(filename):
    """Read a UTF-8 encoded text file and return its contents."""
    with io.open(filename, "r", encoding="utf-8") as f:
        return f.read()


# Get the long description from README.md
current_dir = os.path.abspath(os.path.dirname(__file__))
try:
    long_description = read_file(os.path.join(current_dir, "README.md"))
except (IOError, FileNotFoundError):
    long_description = "A CLI-based folder replication and synchronization tool."

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
        "pywin32>=300; sys_platform == 'win32'",
    ],
    entry_points={
        "console_scripts": [
            "frep=folder_replicator.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Keep this if you want MIT license
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Filesystems",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
)
