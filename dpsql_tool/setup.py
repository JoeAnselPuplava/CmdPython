from setuptools import setup, find_packages

setup(
    name='dpsql',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dpsql=dpsql.__main__:main',
        ],
    },
)