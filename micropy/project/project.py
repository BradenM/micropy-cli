# -*- coding: utf-8 -*-

"""Hosts functionality relating to generation of user projects."""

import json
from pathlib import Path
from typing import Any, Iterator, List, Optional, Sequence, Type

from boltons.queueutils import PriorityQueue

from micropy.config import Config, DictConfigSource
from micropy.logger import Log, ServiceLog
from micropy.project.modules import ProjectModule


class Project(ProjectModule):
    """Micropy Project.

    Args:
        path (str): Path to project root.
        name (str, optional): Name of Project.
            Defaults to None. If none, uses name of current directory.

    """

    def __init__(self, path: str, name: Optional[str] = None, **kwargs: Any):
        self._children: List[Type[ProjectModule]] = []
        self.path: Path = Path(path).absolute()
        self.data_path: Path = self.path / '.micropy'
        self.info_path: Path = self.path / 'micropy.json'
        self.cache_path: Path = self.data_path / '.cache'
        self._context = Config(source_format=DictConfigSource)

        self.name: str = name or self.path.name
        self._config: Config = Config(self.info_path,
                                      default={'name': self.name},
                                      should_sync=lambda *a: self.exists)
        self.log: ServiceLog = Log.add_logger(self.name, show_title=False)

    def __getattr__(self, name: str) -> Any:
        results = iter([c.resolve_hook(name) for c in self._children])
        for res in results:
            if res is not None:
                self.log.debug(f"Hook Resolved: {name} -> {res}")
                return res
        return self.__getattribute__(name)

    @property
    def exists(self) -> bool:
        """Whether this project exists.

        Returns:
            bool: True if it exists

        """
        return self.info_path.exists()

    @property
    def config(self) -> Config:
        """Project Configuration.

        Returns:
            Config: Dictionary of Project Config Values

        """
        return self._config

    @config.setter
    def config(self, value: dict) -> Config:
        """Sets active config.

        Args:
            value (dict): Value to set.

        Returns:
            Config: Current config

        """
        self._config = Config(self.info_path, default=value)
        return self._config

    @property
    def context(self):
        """Project context used in templates.

        Returns:
            dict: Current context

        """
        return self._context

    def _set_cache(self, key, value):
        """Set key in Project cache.

        Args:
            key (str): Key to set
            value (obj): Value to set

        """
        if not self.cache_path.exists():
            self.cache_path.write_text("{}")
        data = json.loads(self.cache_path.read_text())
        data[key] = value
        with self.cache_path.open('w+') as f:
            json.dump(data, f)

    def _get_cache(self, key):
        """Retrieve value from Project Cache.

        Args:
            key (str): Key to retrieve

        Returns:
            obj: Value at key

        """
        if not self.cache_path.exists():
            return None
        data = json.loads(self.cache_path.read_text())
        value = data.pop(key, None)
        return value

    def iter_children_by_priority(self) -> Iterator[Type[ProjectModule]]:
        """Iterate project modules by priority

        Yields:
            the next child item
        """
        pq = PriorityQueue()
        for i in self._children:
            pq.add(i, i.PRIORITY)
        more = pq.peek(default=False)
        while more:
            yield pq.pop()
            more = pq.peek(default=False)

    def add(self, component, *args, **kwargs):
        """Adds project component.

        Args:
            component (Any): Component to add.

        """
        self.log.debug(f'adding module: {type(component).__name__}')
        child = component(*args, parent=self, log=self, **kwargs)
        self._children.append(child)
        if hasattr(child, 'context'):
            self.context.merge(child.context)

    def remove(self, component):
        """Removes project component.

        Args:
            component (Any): Component to remove.

        """
        child = next(i for i in self._children if isinstance(i, component))
        self._children.remove(child)

    def load(self, **kwargs: Any) -> 'Project':
        """Loads all components in Project.

        Returns:
            Current Project Instance

        """
        self.name = self._config.get('name')
        self.data_path.mkdir(exist_ok=True)
        for child in self.iter_children_by_priority():
            child.load(**kwargs)
        return self

    def create(self):
        """Creates new Project.

        Returns:
            Path: Path relative to current active directory.

        """
        self.log.title(f"Initiating $[{self.name}]")
        self.data_path.mkdir(exist_ok=True, parents=True)
        ignore_data = self.data_path / '.gitignore'
        ignore_data.write_text('*')
        self.log.debug(f"Generated Project Context: {self.context}")
        for child in self.iter_children_by_priority():
            self.config.merge(child.config)
            child.create()
        self.info_path.touch()
        self.config.sync()
        self.log.success(f"Project Created!")
        return self.path.relative_to(Path.cwd())

    def update(self):
        """Updates all project components.

        Returns:
            Current active project.

        """
        self.log.debug("Updating all project modules...")
        for child in self.iter_children_by_priority():
            child.update()
        return self
