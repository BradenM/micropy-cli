# -*- coding: utf-8 -*-

import abc
from functools import partial, wraps

"""Project Packages Module Abstract Implementation"""


class ProjectModule(metaclass=abc.ABCMeta):

    _hooks = []

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        if parent:
            for hook in ProjectModule._hooks:
                setattr(parent, hook.__name__, partial(hook, self))
        self._parent = parent

    @property
    def hooks(self):
        return self._hooks

    @classmethod
    def method_hook(cls, func):
        cls._hooks.append(func)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

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
