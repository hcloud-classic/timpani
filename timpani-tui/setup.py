from setuptools import find_packages, setup


setup(
    name="Timpani Python Dialog",
    version='0.0.1',
    description='Python Dialog for Timpani',
    packages=find_packages(exclude=['test', 'test.*']),
    install_requires=[
        'future>=0.14.0; python_version<"3"',
        'futures; python_version>="3"',
        'ujson<=1.35; platform_system!="Windows"',
        'pythondialog',
        'alembic'
    ],
    entry_points={
        'console_scripts': [
            'timpani-tui=timpani.run:main'
        ]
    },
    zip_safe=True
)