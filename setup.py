from setuptools import setup, find_packages
import os

try:
    with open("README.md", "r") as f:
        long_description = f.read()
except FileNotFoundError:
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
    packages=find_packages(),
    install_requires=[
        "watchdog",
        "pywin32; sys_platform == 'win32'",
    ],
    entry_points={
        "console_scripts": [
            "frep=folder_replicator.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
)
