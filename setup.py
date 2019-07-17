#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'micropy-cli'
DESCRIPTION = 'Command line Application for automating Micropython project \
    setup and management in Visual Studio Code.'
URL = 'https://github.com/BradenM/micropy-cli'
AUTHOR = 'Braden Mars'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '1.1.0'  # Update via bumpversion

# Required Packages
REQUIRED = [
    'click',
    'questionary',
    'rshell',
    'colorama ; platform_system=="Windows"',
    'jsonschema',
    'jinja2',
    'requests',
    'tqdm'
]

EXTRAS = {}


here = os.path.abspath(os.path.dirname(__file__))

# Description
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),

    entry_points={
        'console_scripts': ['micropy=micropy.cli:cli'],
    },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='GNU GPLv3',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: MicroPython',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Embedded Systems'
    ],
)
