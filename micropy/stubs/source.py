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
from contextlib import ExitStack, contextmanager
from functools import partial, reduce
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ContextManager, Optional, Union, cast

import attrs
import micropy.exceptions as exc
from micropy import utils
from micropy.logger import Log
from micropy.utils.types import PathStr
from typing_extensions import Protocol

if TYPE_CHECKING:
    from micropy.stubs.repo import StubRepository


class LocateStrategy(Protocol):
    @abc.abstractmethod
    def prepare(self, location: PathStr) -> Union[PathStr, tuple[PathStr, Callable[..., Any]]]:
        ...


logger = Log.add_logger(__name__, show_title=False)


@attrs.define
class StubSource:
    """Handles sourcing stubs."""

    locators: list[LocateStrategy] = attrs.field()
    location: Optional[PathStr] = attrs.field(default=None)

    @locators.default
    def _default_locators(self: StubSource) -> list[LocateStrategy]:
        return [RemoteStubLocator(), StubInfoSpecLocator()]

    def _do_locate(self, stack: ExitStack, path: PathStr, locator: LocateStrategy) -> PathStr:
        logger.debug(f"running (strategy:{locator}) @ (location:{path})")
        response = locator.prepare(path)
        parts = iter(response if isinstance(response, tuple) else (response,))
        path = next(parts, path)
        teardown = next(parts, None)
        if teardown:
            logger.debug(f"adding teardown callback for: {locator}")
            stack.callback(teardown)
        logger.debug(f"results of (strategy:{locator}) -> (location:{path})")
        return path

    @contextmanager
    def ready(self, location: Optional[PathStr] = None) -> ContextManager[PathStr]:
        """Yields prepared Stub Source.

        Allows StubSource subclasses to have a preparation
        method before providing a local path to itself.

        Yields:
            Resolved PathLike object to stub source

        """
        with ExitStack() as stack:
            reducer = cast(
                Callable[[PathStr, LocateStrategy], PathStr], partial(self._do_locate, stack)
            )
            path = reduce(reducer, self.locators, location or self.location)
            yield path


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


@attrs.define
class RepoStubLocator(LocateStrategy):

    repo: StubRepository = attrs.field(repr=False)

    def prepare(self, location: PathStr) -> Union[PathStr, tuple[PathStr, Callable[..., Any]]]:
        if not self.repo:
            return location
        try:
            source = self.repo.resolve_package(location)
        except exc.StubNotFound as e:
            logger.debug(f"{self}: {location} not found in repo, skipping... (exc: {e})")
            return location
        else:
            return source.url


def get_source(location, **kwargs):
    """Factory for StubSource Instance.

    Deprecated. Todo: Remove.

    Args:
        location (str): PathLike object or valid URL

    Returns:
        obj: Either Local or Remote StubSource Instance

    """
    return StubSource(**kwargs, location=location)
