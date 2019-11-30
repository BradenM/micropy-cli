# -*- coding: utf-8 -*-

"""Configuration files and interfaces for them."""

from .config import Config
from .config_json import JSONConfigSource

__all__ = ["Config", "JSONConfigSource"]
