from setuptools import setup, find_packages

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
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Ajaykr2109/ExtFileReplicator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)
