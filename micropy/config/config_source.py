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

    @contextlib.contextmanager
    def _handle_cleanup(self):
        with contextlib.ExitStack() as stack:
            stack.push(self)
            yield
            # any validation occurs here
            # if everything is good, keep the config and continue
            stack.pop_all()

    @abc.abstractmethod
    def save(self, content: Any) -> Any:
        """Method to save config"""

    @abc.abstractmethod
    def process(self) -> dict:
        """Read and process config file.

        Returns:
            dict: Config file content

        """

    @abc.abstractmethod
    def prepare(self) -> Any:
        """Method to prepare on enter"""

    def __enter__(self) -> dict:
        self.prepare()
        with self._handle_cleanup():
            self._config = self.process()
        return self._config

    def __exit__(self, *args):
        self.save(self._config)
