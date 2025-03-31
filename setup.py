from setuptools import setup, find_packages
import io
import os

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="folder-replicator",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        'watchdog>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'folder-replicate=folder_replicator.cli:main',
            'frep=folder_replicator.cli:main',
        ],
    },
    python_requires='>=3.6',

    author="ajay2109",
    description="Folder replication tool with VCS-like capabilities",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/Ajaykr2109/ExtFileReplicator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)
