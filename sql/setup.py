from setuptools import setup, find_packages

setup(
    name='dpsql',
    version='0.1',
    packages=find_packages(),
    # packages=['sql', 'sql.snsql', 'sql.snsql.sql'],
    entry_points={
        'console_scripts': [
            'dpsql=snsql.sql.__main__:main'
        ],
    },
)