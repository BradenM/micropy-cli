# -*- coding: utf-8 -*-

from .config_source import ConfigSource


class DictConfigSource(ConfigSource):

    def __init__(self, config: dict = {}):
        """Dict Config Source.

        Args:
            config (dict, optional): Initial Config.
                Defaults to {}.

        """
        super().__init__(initial_config=config)

    @property
    def exists(self) -> bool:
        return any(self.config.keys())

    def process(self) -> dict:
        return self.config

    def prepare(self):
        return super().prepare()

    def save(self, content: dict) -> dict:
        return content
