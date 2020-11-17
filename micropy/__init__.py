# -*- coding: utf-8 -*-

"""Micropy Cli.

Micropy Cli is a project management/generation tool for writing Micropython
code in modern IDEs such as VSCode. Its primary goal is to automate the
process of creating a workspace complete with:

Linting compatible with Micropython,
VSCode Intellisense,
Autocompletion,
Dependency Management,
VCS Compatibility
and more.

"""

from micropy import data, lib, project, stubs, utils

from .main import MicroPy

__author__ = """Braden Mars"""
__version__ = '3.5.0.rc.1'

__all__ = ["MicroPy", "data", "lib", "project", "stubs", "utils"]
