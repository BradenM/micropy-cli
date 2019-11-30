# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Any, Callable, Optional, Type, Union

from boltons import iterutils

from micropy import utils
from micropy.logger import Log, ServiceLog

from .config_json import JSONConfigSource
from .config_source import ConfigSource

"""Config Interface"""


class Config:
    """Configuration File Interface.

    Automatically syncs config in memory
    with config saved to disk.

    Args:
        path (Path): Path to save file at.
        source_format (ConfigSource, optional): Configuration File Format.
            Defaults to JSONConfigSource.
        default (dict, optional): Default configuration.
                Defaults to {}.
        should_sync: Function to determine whether or not Config should sync.
            Defaults to None.

    """

    def __init__(self,
                 *args: Any,
                 source_format: Type[ConfigSource] = JSONConfigSource,
                 default: dict = {},
                 should_sync: Optional[Callable[..., bool]] = None):
        self.log: ServiceLog = Log.add_logger(f"{__name__}")
        self.should_sync = should_sync or (lambda *args: True)
        self._config = deepcopy(default)
        self.format = source_format
        self._source: ConfigSource = self.format(*args)
        self.sync()

    @property
    def source(self) -> ConfigSource:
        return self._source

    @source.setter
    def source(self, value: Any) -> ConfigSource:
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
        """Sync in-memory config with disk.

        Returns:
            dict: updated config

        """
        if not self.should_sync():
            self.log.debug("sync blocked!")
            return self.config
        with self.source as file_config:
            utils.merge_dicts(self._config, file_config)
            utils.merge_dicts(file_config, self._config)
        self.log.debug('config synced!')
        return self.config

    def merge(self, config: Union[dict, 'Config'], sync: bool = True) -> dict:
        """Merge current config with another.

        Args:
            config (Union[dict,Config]): Config to merge with
            sync (bool, optional): Sync after merging.
                Defaults to True.

        Returns:
            dict: updated config

        """
        _config = config
        if isinstance(config, Config):
            _config = config.config
        utils.merge_dicts(self._config, _config)
        with self.source as file_cfg:
            utils.merge_dicts(self._config, file_cfg)
        if sync:
            return self.sync()
        return self.config

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve config value.

        Args:
            key (str): Key (in dot-notation) of value to return.
            default (Any, optional): Default value to return.
                Defaults to None.

        Returns:
            Any: Value at key given

        """
        key_path = key.split('.')
        value = iterutils.get_path(self.config, key_path, default=default)
        return value

    def set(self, key: str, value: Any) -> Any:
        """Set config value.

        Args:
            key (str): Key (in dot-notation) to update.
            value (Any): Value to set

        Returns:
            Any: Updated config

        """
        full_path = tuple(i for i in key.split('.'))
        path = full_path[:-1]
        p_key = full_path[-1]
        remapped = iterutils.remap(self._config, lambda p, k, v: (
            k, value) if p == path and k == p_key else (k, v))
        self._config = remapped
        self.log.debug(f"set config value [{key}] -> {value}")
        return self.sync()
