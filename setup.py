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
    version="1.1.1",
    author="ajaykr2109_nowStack",
    author_email="chaturvedikraj2109@gmail.com",
    description="A powerful folder synchronization tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ajaykr2109/ExtFileReplicator",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    install_requires=[
        "watchdog>=6.0.0",
        "lockfile>=0.12.2",
        "daemon>=1.2; sys_platform != 'win32'",
        "pywin32>=300; sys_platform == 'win32'",
        "PyQt6>=6.6.1",
        "QDarkStyle>=3.2.0",
    ],
    entry_points={
        "console_scripts": [
            "frep=folder_replicator.cli:main",
            "frep-gui=folder_replicator.gui:run_gui"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Filesystems",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
    ],
    include_package_data=True,
    zip_safe=False,
)
