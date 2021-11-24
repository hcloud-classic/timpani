#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='timpani_filemanager',
    version='2.0.1',
    description='[timpani] File Management ',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[
        'nameko==3.0.0rc6',
        'paramiko',
        'scp'
    ],
    entry_points={
    },

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[test]
    extras_require={
        'test': ['pylint', 'pycodestyle', 'pyflakes', 'pytest', 'mock', 'pytest-cov', 'coverage'],
    },
    zip_safe=True
)
