#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='timpani_dbmanager',
    version='0.0.1',
    description='[timpani] DB Management',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[
        'nameko',
        'future>=0.14.0; python_version<"3"',
        'futures; python_version>="3"',
        'ujson<=1.35; platform_system!="Windows"',
    ],
    entry_points={
        'console_scripts': [
           'framework_db_test=db_test.run:main',
        ]
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
