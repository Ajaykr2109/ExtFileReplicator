from setuptools import setup, find_packages

setup(
    name="folder_replicator",
    version="0.1",
    author="Ajay Kr Chaturvedi",
    description="A folder replication tool with VCS-like capabilities",
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
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
