# -*- coding: utf-8 -*-


from pathlib import Path
from typing import List, Optional, Tuple, Union

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
        self.is_local = True

    @property
    def path(self) -> Path:
        return self._path

    def __enter__(self) -> Union[Path, List[Tuple[Path, Optional[Path]]]]:
        """Determines appropriate path.

        Returns:
            Path to package root or list of files.

        """
        return self.path
