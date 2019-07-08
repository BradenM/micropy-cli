# -*- coding: utf-8 -*-

"""
micropy.data
~~~~~~~~~~~~~~

This module is merely to provide an easy method of locating
data files used by MicropyCli
"""

from pathlib import Path

MOD_PATH = Path(__file__).parent
PATH = MOD_PATH.resolve()
SCHEMAS = PATH / 'schemas'

__all__ = ["PATH", "SCHEMAS"]
