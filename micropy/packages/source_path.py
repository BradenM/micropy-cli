# -*- coding: utf-8 -*-


from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, List, Optional, Tuple, Union

from micropy import utils

from .package import Package
from .source import DependencySource


class LocalDependencySource(DependencySource):

    def __init__(self, package: Package, path: Path):
        super().__init__(package)
        self._path = path

    def __enter__(self) -> Path:
        if self._path.is_file():
            return self._path
        _root = self.get_root(self._path)
        if _root:
            return _root
        return self._path
