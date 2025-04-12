import os
import sys
from setuptools import setup, find_packages


def main():
    setup(
        name="ext_folder_replicator",
        version="1.1.1",
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                'frep=folder_replicator.cli:main',
                'frep-gui=folder_replicator.gui:run_gui',
            ],
        },
        install_requires=[
            "watchdog>=6.0.0",
            "lockfile>=0.12.2",
            "daemon>=1.2; sys_platform != 'win32'",
            "pywin32>=300; sys_platform == 'win32'",
            "PyQt6>=6.6.1",
            "QDarkStyle>=3.2.0",
        ],
    )


if __name__ == '__main__':
    main()
