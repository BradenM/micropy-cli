# -*- coding: utf-8 -*-

"""Hosts functionality relating to generation of user projects."""

import json
from pathlib import Path

from micropy.logger import Log
from micropy.project.modules import ProjectModule


class Project(ProjectModule):
    """Micropy Project.

    Args:
        path (str): Path to project root.
        name (str, optional): Name of Project.
            Defaults to None. If none, uses name of current directory.

    """

    def __init__(self, path, name=None, **kwargs):
        self._children = []
        self.path = Path(path).absolute()
        self.data_path = self.path / '.micropy'
        self.info_path = self.path / 'micropy.json'
        self.cache_path = self.data_path / '.cache'
        self._context = {}
        self._config = {}

        self.name = name or self.path.name
        self.log = Log.add_logger(self.name, show_title=False)

    def __getattr__(self, name):
        results = iter([c.resolve_hook(name) for c in self._children])
        for res in results:
            if res is not None:
                self.log.debug(f"Hook Resolved: {name} -> {res}")
                return res
        return self.__getattribute__(name)

    @property
    def exists(self):
        """Whether this project exists.

        Returns:
            bool: True if it exists

        """
        return self.info_path.exists()

    @property
    def data(self):
        """Data defined in project info file.

        Returns:
            dict: Dictionary of data

        """
        if self.exists:
            return json.loads(self.info_path.read_text())
        return {}

    @property
    def config(self):
        """Project Configuration.

        Returns:
            dict: Dictionary of Project Config Values

        """
        self._config = {
            'name': self.name
        }
        for child in self._children:
            self._config = {**self._config, **child.config}
        return self._config

    @config.setter
    def config(self, value):
        """Sets active config.

        Args:
            value (dict): Value to set.

        Returns:
            dict: Current config

        """
        self._config = value
        return self._config

    @property
    def context(self):
        """Project context used in templates.

        Returns:
            dict: Current context

        """
        for child in self._children:
            child_context = getattr(child, 'context', {})
            self._context = {**self._context, **child_context}
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

    def add(self, component):
        """Adds project component.

        Args:
            component (Any): Component to add.

        """
        self._children.append(component)
        component.parent = self
        component.log = self.log

    def remove(self, component):
        """Removes project component.

        Args:
            component (Any): Component to remove.

        """
        self._children.remove(component)
        component.parent = None

    def to_json(self):
        """Dumps project to data file."""
        with self.info_path.open('w+') as f:
            data = json.dumps(self.config, indent=4)
            f.write(data)

    def load(self, **kwargs):
        """Loads all components in Project.

        Returns:
            Current Project Instance

        """
        self.name = self.data.get("name", self.name)
        self.config = self.data.get("config", self.config)
        self.data_path.mkdir(exist_ok=True)
        for child in self._children:
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
        for child in self._children:
            child.create()
        self.to_json()
        self.log.success(f"Project Created!")
        return self.path.relative_to(Path.cwd())

    def update(self):
        """Updates all project components.

        Returns:
            Current active project.

        """
        self.log.debug("Updating all project modules...")
        for child in self._children:
            child.update()
        return self
