# -*- coding: utf-8 -*-


from pathlib import Path

from .package import Package
from .source import DependencySource


class LocalDependencySource(DependencySource):
    """Dependency Source that is available locally.

    Args:
        package (Package): Package source points too.
        path (Path): Path to package.

    """

    def __init__(self, package: Package, path: Path):
        super().__init__(package)
        self._path = path

    def __enter__(self) -> Path:
        """Determines appropriate path.

        Returns:
            Path: Path to package root.

        """
        if self._path.is_file():
            return self._path
        _root = self.get_root(self._path)
        if _root:
            return _root
        return self._path
