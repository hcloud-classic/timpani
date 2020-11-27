#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='timpani_system',
    version='0.0.1',
    description='[timpani] System Base Information Colletor ',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[
        'nameko',
        'distro',
        'py-dmidecode'
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
