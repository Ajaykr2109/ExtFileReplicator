from setuptools import setup, find_packages
import io
import os
import site
import sys


def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


try:
    long_description = read_file("README.md")
except (IOError, FileNotFoundError):
    long_description = "A powerful folder synchronization tool"

setup(
    name="ext_folder_replicator",
    version=["version"],
    author="ajaykr2109_nowStack",
    author_email="chaturvedikraj2109@gmail.com",
    description="A powerful folder synchronization tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ajaykr2109/ExtFileReplicator",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.7",
    install_requires=[
        "watchdog>=2.1.0",
        "lockfile>=0.12.2",
    ] + (
        ["daemon>=1.2"] if sys.platform != "win32" else ["pywin32>=300"]
    ),
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
    include_package_data=True,
    zip_safe=False,
)
