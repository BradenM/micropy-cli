# -*- coding: utf-8 -*-

"""
micropy.stubs
~~~~~~~~~~~~~~

This module contains all functionality relating
to stub files/frozen modules and their usage in MicropyCli
"""

from . import source
from .stubs import StubManager

__all__ = ['StubManager', 'source']
