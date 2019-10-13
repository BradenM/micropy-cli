#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'micropy-cli'
DESCRIPTION = ('Micropython Project Management Tool with VSCode support, '
               'Linting, Intellisense, Dependency Management, and more!')
URL = 'https://github.com/BradenM/micropy-cli'
AUTHOR = 'Braden Mars'
AUTHOR_EMAIL = "bradenmars@bradenmars.me"
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '3.0.0'  # Update via bump2version
PROJECT_URLS = {
    "Bug Reports": "https://github.com/BradenM/micropy-cli/issues",
    "Documentation": "https://micropy-cli.readthedocs.io",
    "Source Code": URL,
}
KEYWORDS = (
    "micropython stubs linting intellisense "
    "autocompletion vscode visual-studio-code "
    "ide microcontroller"
)

# Required Packages
REQUIRED = [
    'click>=7',
    'questionary',
    'rshell',
    'colorama ; platform_system=="Windows"',
    'jsonschema',
    'jinja2',
    'requests',
    'tqdm',
    'requirements-parser',
    'packaging',
    'cachier'
]

EXTRAS = {
    'create_stubs': ['pyminifier==2.1']
}


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
    author_email=AUTHOR_EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    project_urls=PROJECT_URLS,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),

    entry_points={
        'console_scripts': ['micropy=micropy.cli:cli'],
    },
    keywords=KEYWORDS,
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: MicroPython',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Build Tools'
    ],
)
