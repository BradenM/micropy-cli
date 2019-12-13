# -*- coding: utf-8 -*-


import shutil
from pathlib import Path
from tempfile import mkdtemp
from typing import Any, Callable, List, Optional, Tuple, Union


from micropy import utils
from micropy.exceptions import RequirementNotFound

from .package import Package
from .source import DependencySource


class PackageDependencySource(DependencySource):
    """Dependency Source for pypi packages.

    Args:
        package (Package): Package source points too.
        format_desc: Callback to format progress bar description.
            Defaults to None.

    """
    repo: str = "https://pypi.org/pypi/{name}/json"

    def __init__(self, package: Package,
                 format_desc: Optional[Callable[..., Any]] = None):
        super().__init__(package)
        try:
            utils.ensure_valid_url(self.repo_url)
        except Exception:
            raise RequirementNotFound(
                f"{self.repo_url} is not a valid url!", package=self.package)
        else:
            self._meta: dict = utils.get_package_meta(
                str(self.package),
                self.repo_url
            )
            self.format_desc = format_desc or (lambda n: n)

    @property
    def repo_url(self) -> str:
        _url = self.repo.format(name=self.package.name)
        return _url

    @property
    def source_url(self) -> str:
        return self._meta.get('url', None)

    @property
    def file_name(self) -> str:
        return utils.get_url_filename(self.source_url)

    def fetch(self) -> bytes:
        """Fetch package contents into memory.

        Returns:
            bytes: Package archive contents.

        """
        self.log.debug(f"fetching package: {self.file_name}")
        desc = self.format_desc(self.file_name)
        content = utils.stream_download(self.source_url, desc=desc)
        return content

    def __enter__(self) -> Union[Path, List[Tuple[Path, Path]]]:
        """Prepare Pypi package for installation.

        Extracts the package into a temporary directory then
        generates stubs for type hinting.
        This helps with intellisense.

        If the dependency is a module, a list
        of tuples with the file and stub path, respectively,
        will be returned. Otherwise, the path to the package
        root will be returned.

        Returns:
            Root package path or list of files.

        """
        self.tmp_path = Path(mkdtemp())
        with self.handle_cleanup():
            path = utils.extract_tarbytes(self.fetch(), self.tmp_path)
            stubs = self.generate_stubs(path)
            pkg_root = self.get_root(path)
        return pkg_root or stubs

    def __exit__(self, *args):
        shutil.rmtree(self.tmp_path, ignore_errors=True)
        return super().__exit__(*args)
