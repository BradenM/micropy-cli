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

from __future__ import annotations

from micropy.main import MicroPy
from micropy.utils._compat import metadata

__version__ = metadata.version("micropy-cli")
