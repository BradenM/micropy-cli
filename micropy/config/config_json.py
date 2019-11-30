# -*- coding: utf-8 -*-

import json
from pathlib import Path

from .config_source import ConfigSource


class JSONConfigSource(ConfigSource):
    """JSON Config File Source

    Args:
        path (Path): Path to save config too.
    """

    def __init__(self, path: Path):
        super().__init__(path)

    def process(self) -> dict:
        content = super().process()
        if not content:
            return {}
        config = json.loads(content)
        return config

    def save(self, config: dict) -> dict:
        content = json.dumps(self.config, indent=4)
        return super().save(content)
