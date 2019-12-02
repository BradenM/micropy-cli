# -*- coding: utf-8 -*-


from contextlib import AbstractContextManager, ExitStack, contextmanager
from pathlib import Path
from typing import List, Optional, Tuple

from boltons import fileutils

from micropy import utils
from micropy.logger import Log, ServiceLog

from .package import Package


class DependencySource(AbstractContextManager):
    """Base class for managing dependency sources.

    Args:
        package (Package): package the source points too.

    """
    _ignore_stubs: List[str] = ['setup.py', '__version__', 'test_']

    def __init__(self, package: Package):
        self.is_local = False
        self._package = package
        self.log: ServiceLog = Log.add_logger(repr(self))

    @property
    def package(self) -> Package:
        return self._package

    @contextmanager
    def handle_cleanup(self):
        with ExitStack() as stack:
            stack.push(self)
            yield
            # no errors, continue on
            stack.pop_all()

    def get_root(self, path: Path) -> Optional[Path]:
        """Determines package root if it has one.

        Args:
            path (Path): Path to check

        Returns:
            bool: True if is package

        """
        init = next(path.rglob('__init__.py'), None)
        if init:
            return init.parent
        return None

    def generate_stubs(self, path: Path) -> List[Tuple[Path, Path]]:
        """Generate Stub Files from a package.

        Args:
            path (Path): Path to package.

        Returns:
            List[Tuple[Path, Path]]: List of tuples containing
                 a path to the original file and stub, respectively.

        """
        py_files = fileutils.iter_find_files(str(path), patterns='*.py', ignored=self._ignore_stubs)
        stubs = [utils.generate_stub(f) for f in py_files]
        return stubs

    def __enter__(self):
        """Method to prepare source."""

    def __exit__(self, *args):
        return super().__exit__(*args)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.package}>"
