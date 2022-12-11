"""
micropy.stubs.source
~~~~~~~~~~~~~~

This module contains abstractions for handling stub sources
and their location.
"""

from __future__ import annotations

import abc
import shutil
import tempfile
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Any, Callable, ContextManager, Iterable, Optional, Union

import attrs
from micropy import utils
from micropy.logger import Log
from micropy.utils.types import PathStr
from typing_extensions import Protocol


class LocateStrategy(Protocol):
    @abc.abstractmethod
    def prepare(self, location: PathStr) -> Union[PathStr, tuple[PathStr, Callable[..., Any]]]:
        ...


logger = Log.add_logger(__name__)


@attrs.define
class StubSource:
    """Handles sourcing stubs."""

    location: PathStr = attrs.field()
    locators: list[LocateStrategy] = attrs.field()

    @locators.default
    def _default_locators(self: StubSource) -> list[LocateStrategy]:
        return [RemoteStubLocator(), StubInfoSpecLocator()]

    @contextmanager
    def ready(self) -> ContextManager[PathStr]:
        """Yields prepared Stub Source.

        Allows StubSource subclasses to have a preparation
        method before providing a local path to itself.

        Yields:
            Resolved PathLike object to stub source

        """
        path = self.location
        teardown = lambda: None
        for locator in self.locators:
            logger.debug(f"running (strategy:{locator}) @ (location:{path})")
            response = locator.prepare(path)
            parts = iter(response if isinstance(response, Iterable) else (response,))
            path = next(parts, path)
            teardown = next(parts, teardown)
            logger.debug(f"results of (strategy:{locator}) -> (location:{path})")
        yield path
        if teardown:
            teardown()


@attrs.define
class StubInfoSpecLocator(LocateStrategy):
    def prepare(self, location: PathStr) -> PathStr:
        info_path = next(Path(location).rglob("info.json"), None)
        return location if info_path is None else info_path.parent


@attrs.define
class RemoteStubLocator(LocateStrategy):
    """Stub Source for remote locations."""

    def _unpack_archive(self, file_bytes: bytes, path: PathStr) -> PathStr:
        """Unpack archive from bytes buffer.

        Args:
            file_bytes (bytes): Byte array to extract from
                Must be from tarfile with gzip compression
            path (str): path to extract file to

        Returns:
            path: path extracted to

        """
        path = Path(utils.extract_tarbytes(file_bytes, path))
        output = next(path.iterdir())
        return output

    def prepare(self, location: PathStr) -> tuple[PathStr, Optional[Callable[..., Any]]] | PathStr:
        """Retrieves and unpacks source.

        Prepares remote stub resource by downloading and
        unpacking it into a temporary directory.
        This directory is removed via the returned teardown.

        """
        if not utils.is_url(location):
            logger.debug(f"{self}: {location} not viable, skipping...")
            return location
        tmp_dir = tempfile.mkdtemp()
        tmp_path = Path(tmp_dir)
        filename = utils.get_url_filename(location).split(".tar.gz")[0]
        _file_name = "".join(logger.iter_formatted(f"$B[{filename}]"))
        content = utils.stream_download(location, desc=f"{logger.get_service()} {_file_name}")
        source_path = self._unpack_archive(content, tmp_path)
        teardown = partial(shutil.rmtree, tmp_path)
        return source_path, teardown


def get_source(location, **kwargs):
    """Factory for StubSource Instance.

    Deprecated. Todo: Remove.

    Args:
        location (str): PathLike object or valid URL

    Returns:
        obj: Either Local or Remote StubSource Instance

    """
    return StubSource(location, **kwargs)
