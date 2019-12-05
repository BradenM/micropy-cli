# -*- coding: utf-8 -*-

"""Config Abstract."""

import abc
import contextlib
from typing import Any

from micropy.logger import Log, ServiceLog


class ConfigSource(contextlib.AbstractContextManager, metaclass=abc.ABCMeta):
    """Abstract Base Class for Config Sources.

    Args:
        initial_config (dict, optional): Initial config values.
            Defaults to {}.

    """

    def __init__(self, initial_config: dict = {}):
        self._config: dict = initial_config
        self.log: ServiceLog = Log.add_logger(__name__)

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

    @abc.abstractproperty
    def exists(self) -> bool:
        """Property to check if source exists."""

    @abc.abstractmethod
    def save(self, content: Any) -> Any:
        """Method to save config."""

    @abc.abstractmethod
    def process(self) -> dict:
        """Read and process config file.

        Returns:
            dict: Config file content

        """

    @abc.abstractmethod
    def prepare(self) -> Any:
        """Method to prepare on enter."""

    def __enter__(self) -> dict:
        self.prepare()
        self._config = self.process()
        return self._config

    def __exit__(self, *args):
        self.save(self._config)
