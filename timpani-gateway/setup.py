#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='timpani-gateway',
    version='0.0.1',
    description='Timpani Web Interface ',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[
        'nameko==v3.0.0-rc6',
        'marshmallow',
        'flask',
        'flask_script',
        'graphene',
        'Flask-GraphQL',
    ],
    extras_require={
        'dev': [
            'pytest==4.5.0',
            'coverage==4.5.3',
            'flake8==3.7.7',
        ],
    },
    zip_safe=True
)
