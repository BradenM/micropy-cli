# -*- coding: utf-8 -*-

from copy import deepcopy
from pathlib import Path
from typing import Any

from boltons import iterutils

from micropy import utils
from micropy.logger import Log, ServiceLog

from .config_json import JSONConfigSource
from .config_source import ConfigSource


class Config:

    def __init__(
            self,
            path: Path,
            source_format: ConfigSource = JSONConfigSource,
            default: dict = {}):
        """Configuration File Interface

        Args:
            path (Path): Path to save file at.
            source_format (ConfigSource, optional): Configuration File Format.
                Defaults to JSONConfigSource.
            default (dict, optional): Default configuration.
                 Defaults to {}.
        """
        self.log: ServiceLog = Log.add_logger(f"{__name__}({path.name})")
        self._config = deepcopy(default)
        self.format = source_format
        self._source: ConfigSource = self.format(path)
        self.sync()

    @property
    def source(self) -> ConfigSource:
        return self._source

    @source.setter
    def source(self, value: Path) -> ConfigSource:
        self._source = self.format(value)
        return self._source

    @property
    def config(self) -> dict:
        return self._config

    @config.setter
    def config(self, value: dict) -> dict:
        with self.source:
            self.source.config = value
            self._config = value
        return self.sync()

    def sync(self) -> dict:
        """Load config from file

        Returns:
            dict: updated config
        """
        with self.source as file_config:
            utils.merge_dicts(self._config, file_config)
            utils.merge_dicts(file_config, self._config)
        self.log.debug("configuration synced!")
        return self.config

    def merge(self, config: dict) -> dict:
        """Merge current config with another

        Args:
            config (dict): config to merge with

        Returns:
            dict: updated config
        """
        utils.merge_dicts(self._config, config)
        with self.source as file_cfg:
            utils.merge_dicts(self._config, file_cfg)
        return self.sync()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve config value

        Args:
            key (str): key of config value to retrieve
            default (Any, optional): Default value to return.
                Defaults to None.

        Returns:
            Any: Value at key given
        """
        key_path = key.split('.')
        value = iterutils.get_path(self.config, key_path, default=default)
        return value

    def set(self, key: str, value: Any) -> Any:
        """Set config value

        Args:
            key (str): Key to set in dot notation
            value (Any): Value to set

        Returns:
            Any: Updated config
        """
        full_path = tuple(i for i in key.split('.'))
        path = full_path[:-1]
        key = full_path[-1]
        remapped = iterutils.remap(self._config, lambda p, k, v: (
            k, value) if p == path and k == key else (k, v))
        self._config = remapped
        self.log.debug(f"set config value [{key}] -> {value}")
        return self.sync()
