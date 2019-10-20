# -*- coding: utf-8 -*-

import abc
import inspect
from functools import wraps

from micropy import utils
from micropy.logger import Log

"""Project Packages Module Abstract Implementation"""


class ProjectModule(metaclass=abc.ABCMeta):

    _hooks = []

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
    def hook(cls, *args, **kwargs):
        def _hook(func):
            name = kwargs.get('name', func.__name__)
            hook = next((i for i in cls._hooks if i._name == name), None)
            if not hook:
                hook = HookProxy(name)
                ProjectModule._hooks.append(hook)
            hook.add_method(func, **kwargs)
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return _hook

    def resolve_hook(self, name):
        _hook = None
        for hook in self._hooks:
            if hook._name == name:
                _hook = hook
                _hook.add_instance(self)
        return _hook


class HookProxy:
    def __init__(self, name):
        self.methods = []
        self.instances = []
        self._name = name
        self.log = Log.add_logger(str(self))

    def __call__(self, *args, **kwargs):
        for method, name in self.methods:
            _name = self.get_name(method, kwargs)
            if name == _name:
                _class = utils.get_class_that_defined_method(method)
                instance = next((i for i in self.instances if isinstance(i, _class)))
                self.log.debug(f"{self._name} proxied to [{name}@{instance}]")
                return getattr(instance, method.__name__)(*args, **kwargs)

    def __str__(self):
        name = f"HookProxy({self._name})"
        return name

    def __repr__(self):
        name = f"HookProxy(name={self._name}, methods=[{self.methods}])"
        return name

    def add_method(self, func, **kwargs):
        name = self.get_name(func, kwargs)
        hook = (func, name)
        self.methods.append(hook)
        self.log.debug(f"Method added to proxy: {hook}")
        return hook

    def add_instance(self, inst):
        return self.instances.append(inst)

    def get_name(self, func, params):
        sig = inspect.signature(func)
        _default = {p.name: p.default for p in sig.parameters.values() if p.kind ==
                    p.POSITIONAL_OR_KEYWORD and p.default is not p.empty}
        params = {**_default, **params}
        name = f"_hook__{self._name}__{'__'.join(f'{k}_{v}' for k, v in params.items())}"
        return name
