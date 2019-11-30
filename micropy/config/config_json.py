# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import Any

from .config_source import ConfigSource


class JSONConfigSource(ConfigSource):
    """JSON Config File Source

    Args:
        path (Path): Path to save config too.
    """

    def __init__(self, path: Path):
        super().__init__(path)

    def process(self) -> dict:
        """Load config from JSON file

        Returns:
            dict: config in file
        """
        content = self.file_path.read_text()
        if not content:
            return {}
        config = json.loads(content)
        return config

    def preprocess(self, content: Any) -> str:
        """Preprocess config in memory before writing to file.

        Args:
            content (Any): current config

        Returns:
            str: Content ready to be written to file.
        """
        content = json.dumps(content, indent=4)
        return content

    def save(self, content: str) -> Path:
        """Save current config

        Args:
            content (str): content to write to file.

        Returns:
            Path: path to config file.
        """
        return super().save(content)
