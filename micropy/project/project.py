# -*- coding: utf-8 -*-

"""Hosts functionality relating to generation of user projects."""

from pathlib import Path
from typing import Any, Iterator, List, Optional, Type

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
        self._cache = Config(self.cache_path)
        self._context = Config(source_format=DictConfigSource,
                               default={'datadir': self.data_path})
        self.name: str = name or self.path.name
        default_config = {
            'name': self.name,
        }
        self._config: Config = Config(self.info_path,
                                      default=default_config)
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
            Config: Project Config Instance

        """
        return self._config

    @property
    def context(self) -> Config:
        """Project context used in templates.

        Returns:
            Config: Current context

        """
        return self._context

    @property
    def cache(self) -> Config:
        """Project wide cache.

        Returns:
            Cache instance

        """
        return self._cache

    def iter_children_by_priority(self) -> Iterator[Type[ProjectModule]]:
        """Iterate project modules by priority.

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
        child = component(*args, **kwargs, log=self.log, parent=self)
        self._children.append(child)
        self.log.debug(f'adding module: {type(child).__name__}')

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
            child.create()
        self.info_path.touch()
        self.config.sync()
        self.log.success(f"Project Created!")
        return self.path

    def update(self):
        """Updates all project components.

        Returns:
            Current active project.

        """
        self.log.debug("Updating all project modules...")
        for child in self.iter_children_by_priority():
            child.update()
        return self
