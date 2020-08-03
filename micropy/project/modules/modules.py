# -*- coding: utf-8 -*-

import abc
import inspect
from copy import deepcopy
from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, Type, TypeVar, Union

from micropy import utils
from micropy.config import Config
from micropy.logger import Log, ServiceLog

"""Project Packages Module Abstract Implementation"""

T = TypeVar('T')
ProxyItem = List[Tuple[T, str]]


class ProjectModule(metaclass=abc.ABCMeta):
    """Abstract Base Class for Project Modules."""
    PRIORITY: int = 0
    _hooks: List['HookProxy'] = []

    def __init__(self, parent: Optional['ProjectModule'] = None, log: Optional[ServiceLog] = None):
        self._parent = parent
        self.log = log

    @property
    def parent(self):
        """Component Parent."""
        return self._parent

    @parent.setter
    def parent(self, parent: Type['ProjectModule']) -> Type['ProjectModule']:
        """Sets component parent.

        Args:
            parent (Any): Parent to set

        """
        self._parent = parent
        return self.parent

    @abc.abstractproperty
    def config(self) -> Union[dict, Config]:
        """Config values specific to component."""

    @abc.abstractmethod
    def load(self):
        """Method to load component."""

    @abc.abstractmethod
    def create(self, *args: Any, **kwargs: Any) -> Any:
        """Method to create component."""

    @abc.abstractmethod
    def update(self):
        """Method to update component."""

    def add(self, component: Type['ProjectModule'], *args: Any, **kwargs: Any) -> Any:
        """Adds component.

        Args:
            component (Any): Component to add.

        """

    def remove(self, component: Type['ProjectModule']) -> Any:
        """Removes component.

        Args:
            component (Any): Component to remove.

        """

    @classmethod
    def hook(cls, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """Decorator for creating a Project Hook.

        Allows decorated method to be called from parent
        container.

        Returns:
            Callable: Decorated function.

        """
        def _hook(func: T) -> Callable[..., Any]:
            name = kwargs.get('name', func.__name__)
            hook = next((i for i in cls._hooks if i._name == name), None)
            if not hook:
                hook = HookProxy(name)
                ProjectModule._hooks.append(hook)
            hook.add_method(func, **kwargs)

            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                return func(*args, **kwargs)
            return wrapper
        return _hook

    def resolve_hook(self, name: str) -> Union[Optional['HookProxy'], T]:
        """Resolves appropriate hook for attribute name.

        Args:
            name (str): Attribute name to resolve hook for.

        Returns:
            Optional[HookProxy]: Callable Proxy for ProjectHook.
            NoneType: Name could not be resolved.

        """
        _hook = None
        for hook in self._hooks:
            if hook._name == name:
                _hook = hook
                _hook.add_instance(self)
                if _hook.is_descriptor():
                    return _hook.get()
        return _hook


class HookProxy:
    """Proxy for Project Hooks.

    Allows multiple project hooks with the same name by
    creating individual hooks for any defined permutations
    of kwargs.

    This is accomplished by creating a unique name for each
    permutation proxying the original attribute name to the
    appropriate method determined from the provided kwargs.

    Args:
        name (str): Name of Proxy

    """

    def __init__(self, name: str):
        self.methods: List[ProxyItem[Callable[..., Any]]] = []
        self.instances: List[Type[ProjectModule]] = []
        self._name: str = name
        self.log: ServiceLog = Log.add_logger(str(self))

    def __call__(self, *args, **kwargs):
        proxy_kwargs = deepcopy(kwargs)
        proxy = self.resolve_proxy(**proxy_kwargs)
        if proxy:
            return getattr(*proxy)(*args, **kwargs)

    def __str__(self):
        name = f"HookProxy({self._name})"
        return name

    def __repr__(self):
        name = f"HookProxy(name={self._name}, methods=[{self.methods}])"
        return name

    def resolve_proxy(self, **kwargs: Any) -> (Type[ProjectModule], str):
        """Resolves appropriate instance and method to proxy to.

        If additional kwargs are provided and a proxy is not found,
        the function will continue to remove one kwarg and
        recurse into itself until either a match is found or it runs
        out of kwargs.

        Returns:
            Instance and method name if resolved, otherwise None.

        """
        proxy_kwargs = deepcopy(kwargs)
        for method, name in self.methods:
            _name = self.get_name(method, proxy_kwargs)
            if name == _name:
                instance = self._get_instance(method)
                self.log.debug(f"{self._name} proxied to [{_name}@{instance}]")
                return (instance, method.__name__)
        if proxy_kwargs:
            self.log.debug(
                f'could not resolve proxy: {self._name}[{proxy_kwargs}], broadening search...')
            proxy_kwargs.popitem()
            return self.resolve_proxy(**proxy_kwargs)
        return None

    def _get_instance(self, attr: Callable[..., Any]) -> Optional[Type[ProjectModule]]:
        """Retrieves instance from attribute.

        Args:
            attr (Callable): Attribute to use.

        Returns:
            Instance the attribute belongs to.

        """
        _class = utils.get_class_that_defined_method(attr)
        if _class:
            instance = next((i for i in self.instances if isinstance(i, _class)), None)
            return instance

    def is_descriptor(self) -> bool:
        """Determine if initial method provided is a descriptor."""
        method = self.methods[0][0]
        instance = self._get_instance(method)
        if instance:
            attr = inspect.getattr_static(instance, self._name)
            return inspect.isdatadescriptor(attr)
        return False

    def get(self) -> T:
        """Get initial method descriptor value."""
        instance = self._get_instance(self.methods[0][0])
        self.log.debug(f"{self._name} proxied to [property@{instance}]")
        return getattr(instance, self._name)

    def add_method(self, func: Callable[..., Any], **kwargs: Any) -> ProxyItem[Callable[..., Any]]:
        """Adds method to Proxy.

        Any kwargs provided will be used to generate the unique
        hook name.

        Args:
            func (Callable): Method to add

        Example:
            >>> def test_func(arg1, kwarg1=False):
                    pass

            >>> self.add_method(test_func, {'kwarg1': False})
            (test_func, '_hook__test_func__kwarg1_False')

        Returns:
            Tuple[Callable, str]: Tuple containing method and unique hook name.

        """
        name = self.get_name(func, kwargs)
        hook = (func, name)
        self.methods.append(hook)
        self.log.debug(f"Method added to proxy: {hook}")
        return hook  # type: ignore

    def add_instance(self, inst: Any) -> Any:
        """Add instance to Proxy.

        Args:
            inst (Any): Instance to add.

        """
        return self.instances.append(inst)

    def get_name(self, func: Callable[..., Any], params: Optional[dict] = None) -> str:
        """Generates name from method and provided kwargs.

        Args:
            func (Callable): Method to generate name for.
            params (Dict[Any, Any], optional): Any kwargs to update the defaults with.
                Defaults to None. If none, uses default kwargs.

        Returns:
            str: Generated name

        """
        params = params or {}
        sig = inspect.signature(func)
        _default = {p.name: p.default for p in sig.parameters.values() if p.kind ==
                    p.POSITIONAL_OR_KEYWORD and p.default is not p.empty}
        params = {**_default, **params}
        name = f"_hook__{self._name}__{'__'.join(f'{k}_{v}' for k, v in params.items())}"
        return name
