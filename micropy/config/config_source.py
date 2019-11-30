# -*- coding: utf-8 -*-

"""Config Abstract."""

import abc
import contextlib
from pathlib import Path
from typing import Any

from boltons.fileutils import AtomicSaver

from micropy.logger import Log, ServiceLog


class ConfigSource(contextlib.AbstractContextManager, metaclass=abc.ABCMeta):
    """Abstract Base Class for Config Sources.

    Args:
        path (Path): Path to save config too.

    """

    def __init__(self, path: Path):
        self._file_path: Path = path
        self._config: dict = {}
        self.log: ServiceLog = Log.add_logger(__name__)

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
    def config(self) -> dict:
        """Current Config Content."""
        return self._config

    @config.setter
    def config(self, value: dict) -> dict:
        """Set current config content.

        Args:
            value (dict): New value to set

        Returns:
            dict: Current config

        """
        self._config = value
        return self._config

    @contextlib.contextmanager
    def _handle_cleanup(self):
        with contextlib.ExitStack() as stack:
            stack.push(self)
            yield
            # any validation occurs here
            # if everything is good, keep the config and continue
            stack.pop_all()

    @abc.abstractmethod
    def preprocess(self, content: Any) -> str:
        """Preprocess config before saving to file.

        Args:
            content (Any): Content to preprocess

        Returns:
            str: Content to write to file

        """

    @abc.abstractmethod
    def save(self, content: Any) -> Path:
        """Save content to file.

        Args:
            config (Any): Content to save

        """
        content = self.preprocess(content)
        with AtomicSaver(str(self.file_path), text_mode=True) as file:
            file.write(content)
        return self.file_path

    @abc.abstractmethod
    def process(self) -> dict:
        """Read and process config file.

        Returns:
            dict: Config file content

        """

    def __enter__(self) -> dict:
        if not self.file_path.exists():
            self.log.debug(f"creating new config file: {self.file_path}")
            self.file_path.touch()
        with self._handle_cleanup():
            self.log.debug(f'processing config from {self.file_path}')
            self._config = self.process()
        return self._config

    def __exit__(self, *args):
        self.save(self._config)
