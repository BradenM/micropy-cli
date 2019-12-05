# -*- coding: utf-8 -*-

import json
from pathlib import Path

from boltons.fileutils import AtomicSaver

from .config_source import ConfigSource


class JSONConfigSource(ConfigSource):
    """JSON Config File Source.

    Args:
        path (Path): Path to save config too.

    """

    def __init__(self, path: Path):
        super().__init__()
        self._file_path: Path = path

    @property
    def file_path(self) -> Path:
        """Path to config file."""
        return self._file_path

    @file_path.setter
    def file_path(self, value: Path) -> Path:
        """Set config file path.

        Args:
            value (Path): New path to config file

        Returns:
            Path: Path to config file

        """
        self._file_path = value
        return self._file_path

    @property
    def exists(self) -> bool:
        return self.file_path.exists()

    def process(self) -> dict:
        """Load config from JSON file.

        Returns:
            dict: config in file

        """
        content = self.file_path.read_text()
        if not content:
            return {}
        config = json.loads(content)
        return config

    def prepare(self):
        if not self.file_path.exists():
            self.log.debug(f"creating new config file: {self.file_path}")
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.touch()

    def save(self, content: dict) -> Path:
        """Save current config.

        Args:
            content (dict): content to write to file.

        Returns:
            Path: path to config file.

        """
        config = json.dumps(content, indent=4, separators=(',', ': '))
        with AtomicSaver((str(self.file_path)), text_mode=True) as file:
            file.write(config)
        return self.file_path
