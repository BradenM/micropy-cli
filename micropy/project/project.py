# -*- coding: utf-8 -*-

"""Hosts functionality relating to generation of user projects."""

import abc
import json
import shutil
import sys
import tempfile
from pathlib import Path

import requirements

from micropy import utils
from micropy.exceptions import StubError
from micropy.logger import Log
from micropy.project.template import TemplateProvider

from . import modules


class Project(modules.ProjectModule):

    def __init__(self, path, name=None, **kwargs):
        self._children = []
        self.path = Path(path).absolute()
        self.data_path = self.path / '.micropy'
        self.info_path = self.data_path / 'micropy.json'
        self.cache_path = self.data_path / '.cache'

        self.name = name or self.path.name
        self.log = Log.add_logger(self.name, show_title=False)
        self.pkg_data = self.data_path / self.name

    @property
    def exists(self):
        """Whether this project exists

        Returns:
            bool: True if it exists
        """
        return self.info_path.exists()

    @property
    def data(self):
        if self.exists:
            return json.loads(self.info_path.read_text())
        return {}

    @property
    def config(self):
        _config = {
            'name': self.name
        }
        for child in self._children:
            _config = {**_config, **child.config}
        return _config

    @property
    def context(self):
        _context = {}
        for child in self._children:
            child_context = getattr(child, 'context', {})
            _context = {**_context, **child_context}
        return _context

    def _set_cache(self, key, value):
        """Set key in Project cache

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
        """Retrieve value from Project Cache

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
        self._children.append(component)
        component.parent = self
        component.log = self.log

    def remove(self, component):
        self._children.remove(component)
        component.parent = None

    def to_json(self):
        """Dumps project to data file"""
        with self.info_path.open('w+') as f:
            data = json.dumps(self.info, indent=4)
            f.write(data)

    def load(self, **kwargs):
        self.name = self.data.get("name", self.name)
        self.config = self.data.get("config", self.config)
        self.data_path.mkdir(exist_ok=True)
        for child in self._children:
            child.load(**kwargs)
        return self

    def create(self):
        self.log.title(f"Initiating $[{self.name}]")
        self.data_path.mkdir(exist_ok=True, parents=True)
        self.log.debug(f"Generated Project Context: {self.context}")
        for child in self._children:
            child.create()
        return self.path.relative_to(Path.cwd())

    def update(self):
        for child in self._children:
            child.update()
        return self

    def add_stub(self, *args, **kwargs):
        for child in self._children:
            if hasattr(child, 'add_stub'):
                return child.add_stub(*args, **kwargs)

    def add_package(self, *args, **kwargs):
        for child in self._children:
            if hasattr(child, 'add_package'):
                return child.add_package(*args, **kwargs)
