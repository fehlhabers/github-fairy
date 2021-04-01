#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name='github-fairy',
    version='0.1',
    packages=find_packages(),
    scripts=['github-fairy.py'],
    py_modules=['github-fairy'],
    install_requires=[
        'jproperties',
        'requests',
        'keyring',
        'argparse'
    ],
)
