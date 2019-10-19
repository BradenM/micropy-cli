# -*- coding: utf-8 -*-

import abc
from functools import wraps

"""Project Packages Module Abstract Implementation"""


class ProjectModule(metaclass=abc.ABCMeta):

    _hooks = set()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @abc.abstractproperty
    def config(self):
        pass

    @abc.abstractmethod
    def load(self):
        pass

    @abc.abstractmethod
    def create(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    def add(self, component):
        pass

    def remove(self, component):
        pass

    @classmethod
    def hook(cls, func, name=None):
        name = name or func.__name__
        cls._hooks.add(name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def resolve_hook(self, name):
        for hook in self._hooks:
            if hasattr(self, name):
                return getattr(self, name)
