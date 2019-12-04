# -*- coding: utf-8 -*-

import contextlib
from copy import deepcopy
from typing import Any, List, Sequence, Tuple, Type, Union

import dpath
from boltons import iterutils

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

    """

    def __init__(self,
                 *args: Any,
                 source_format: Type[ConfigSource] = JSONConfigSource,
                 default: dict = {}):
        self.log: ServiceLog = Log.add_logger(f"{__name__}")
        self.format = source_format
        self._source: ConfigSource = self.format(*args)
        self._config = deepcopy(default)
        self._do_sync = True
        self._root_key = ''
        if self._source.exists:
            with self._source as src:
                self.log.debug("loaded config values")
                dpath.util.merge(self._config, src, flags=dpath.MERGE_REPLACE)

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

    def root(self, key: str) -> str:
        return self._root_key + key

    def raw(self) -> dict:
        if self._root_key:
            return deepcopy(self.get(self._root_key[:-1], {}))
        return self._config

    def sync(self) -> dict:
        """Sync in-memory config with disk.

        Returns:
            dict: updated config

        """
        if self._do_sync:
            with self.source as src:
                dpath.util.merge(src, self.config, flags=dpath.MERGE_REPLACE)
            self.log.debug('config synced!')
        return self.config

    def parse_key(self, key: str) -> Tuple[Sequence[str], str]:
        """Parses key.

        Splits it into a path and 'final key'
        object. Each key is seperates by a: "/"

        Example:
            >>> self.parse_key('item/subitem/value')
            (('item', 'subitem'), 'value')

        Args:
            key (str): key in dot notation

        Returns:
            Tuple[Sequence[str], str]: Parsed key

        """
        full_path = tuple(i for i in key.split('/'))
        path = full_path[:-1]
        p_key = full_path[-1]
        return (path, p_key)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve config value.

        Args:
            key (str): Key (in dot-notation) of value to return.
            default (Any, optional): Default value to return.
                Defaults to None.

        Returns:
            Any: Value at key given

        """
        try:
            value = dpath.util.get(self.config, self.root(key))
        except KeyError:
            value = default
        finally:
            return value

    def set(self, key: str, value: Any) -> Any:
        """Set config value.

        Args:
            key (str): Key (in dot-notation) to update.
            value (Any): Value to set

        Returns:
            Any: Updated config

        """
        key = self.root(key)
        dpath.set(self._config, key, value)
        self.log.debug(f"set config value [{key}] => {value}")
        return self.sync()

    def add(self, key: str, value: Any) -> Any:
        """Overwrite or add config value.

        Args:
            key: Key to set
            value: Value to add or update too

        Returns:
            Updated config

        """
        key = self.root(key)
        dpath.new(self._config, key, value)
        self.log.debug(f"added config value [{key}] -> {value}")
        return self.sync()

    def pop(self, key: str) -> Any:
        """Delete and return value at key.

        Args:
            key (str): Key to pop.

        Returns:
            Any: Popped value.

        """
        key = self.root(key)
        path, target = self.parse_key(key)
        value = self.get(key)
        remapped = iterutils.remap(self._config, lambda p, k,
                                   v: False if p == path and k == target else True)
        self._config = remapped
        self.log.debug(f"popped config value {value} <- [{key}]")
        return self.sync()

