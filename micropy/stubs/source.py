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
from typing import Any, Callable, Optional, final

from micropy import utils
from micropy.logger import Log
from micropy.utils.types import PathStr


class StubSource(abc.ABC):
    """Abstract Base Class for Stub Sources."""

    location: PathStr

    def __init__(self, location: PathStr, log=None):
        self.location = location
        _name = self.__class__.__name__
        self.log = log or Log.add_logger(_name)

    @abc.abstractmethod
    def prepare(self) -> tuple[PathStr, Optional[Callable[..., Any]]]:
        """Prepares the source."""

    @contextmanager
    def ready(self):
        """Yields prepared Stub Source.

        Allows StubSource subclasses to have a preparation
        method before providing a local path to itself.

        Args:
            path (str, optional): path to stub source.
                Defaults to location.
            teardown (func, optional): callback to execute on exit.
                Defaults to None.

        Yields:
            Resolved PathLike object to stub source

        """
        prep = iter(self.prepare())
        path = next(prep, self.location)
        teardown = next(prep, lambda: None)
        info_path = next(Path(path).rglob("info.json"), None)
        path = Path(info_path.parent) if info_path else path
        yield path
        if teardown:
            teardown()

    def __str__(self):
        _name = self.__class__.__name__
        return f"<{_name}@{self.location}>"


@final
class LocalStubSource(StubSource):
    """Stub Source Subclass for local locations.

    Args:
        path (str): Path to Stub Source

    Returns:
        obj: Instance of LocalStubSource

    """

    def prepare(self) -> tuple[PathStr, Optional[Callable[..., Any]]]:
        return self.location, None

    def __init__(self, path, **kwargs):
        location = utils.ensure_existing_dir(path)
        super().__init__(location, **kwargs)


@final
class RemoteStubSource(StubSource):
    """Stub Source for remote locations.

    Args:
        url (str): URL to Stub Source

    Returns:
        obj: Instance of RemoteStubSource

    """

    def _unpack_archive(self, file_bytes, path):
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

    def prepare(self) -> tuple[PathStr, Optional[Callable[..., Any]]]:
        """Retrieves and unpacks source.

        Prepares remote stub resource by downloading and
        unpacking it into a temporary directory.
        This directory is removed on exit of the superclass
        context manager

        Returns:
            callable: StubSource.ready parent method

        """
        tmp_dir = tempfile.mkdtemp()
        tmp_path = Path(tmp_dir)
        filename = utils.get_url_filename(self.location).split(".tar.gz")[0]
        _file_name = "".join(self.log.iter_formatted(f"$B[{filename}]"))
        content = utils.stream_download(
            self.location, desc=f"{self.log.get_service()} {_file_name}"
        )
        source_path = self._unpack_archive(content, tmp_path)
        teardown = partial(shutil.rmtree, tmp_path)
        return source_path, teardown


def get_source(location, **kwargs):
    """Factory for StubSource Instance.

    Args:
        location (str): PathLike object or valid URL

    Returns:
        obj: Either Local or Remote StubSource Instance

    """
    try:
        utils.ensure_existing_dir(location)
    except NotADirectoryError:
        return RemoteStubSource(location, **kwargs)
    else:
        return LocalStubSource(location, **kwargs)
