# -*- coding: utf-8 -*-

"""
micropy.utils.decorators
~~~~~~~~~~~~~~

This module contains generic decorators
used by MicropyCli
"""

__all__ = ['lazy_property']


def lazy_property(fn):
    attr = '_lazy__' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr):
            setattr(self, attr, fn(self))
        return getattr(self, attr)

    return _lazy_property
