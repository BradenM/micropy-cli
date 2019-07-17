# -*- coding: utf-8 -*-

"""
micropy.stubs.source
~~~~~~~~~~~~~~

This module contains abstractions for handling stub sources
and their location.
"""


import io
import json
import shutil
import tarfile
import tempfile
from contextlib import contextmanager
from functools import partial
from pathlib import Path

import micropy.exceptions as exc
from micropy import utils
from micropy.logger import Log


class StubRepo:
    """Represents a remote repository for stubs

    Args:
        name (str): Repo Name
        location (str): Valid url
        ref (str): path to repo definition file
    """
    repos = set()

    def __init__(self, name, location, path):
        self.name = name
        self.path = path
        self.location = utils.ensure_valid_url(location)
        self.repos.add(self)

    def has_package(self, name):
        """Checks if package is available in repo

        Args:
            name (str): name of package

        Returns:
            bool: True if package is available
        """
        url = self.get_url(name)
        return utils.is_downloadable(url)

    def get_url(self, path):
        """Returns formatted url to provided path

        Args:
            path (str): path to format

        Returns:
            str: formatted url
        """
        url = f"{self.location}/{self.path}/{path}.tar.gz"
        return url

    def search(self, query):
        """Searches repository packages

        Args:
            query (str): query to search by

        Returns:
            [str]: List of matching results
        """
        query = query.strip().lower()
        results = utils.search_xml(self.location, "Key")
        pkgs = [Path(p).name for p in results if self.path in p]
        pkg_names = [p.split(".tar.gz")[0] for p in pkgs]
        results = set([p for p in pkg_names if query in p.lower()])
        return results

    @classmethod
    def resolve_package(cls, name):
        """Attempts to resolve package from all repos

        Args:
            name (str): package to resolve

        Raises:
            StubNotFound: Package could not be resolved

        Returns:
            str: url to package
        """
        results = (r for r in cls.repos if r.has_package(name))
        try:
            repo = next(results)
        except StopIteration:
            raise exc.StubNotFound(name)
        else:
            pkg_url = repo.get_url(name)
            return pkg_url

    @classmethod
    def from_json(cls, content):
        """Create StubRepo Instances from JSON file

        Args:
            file_obj (str or bytes): json content

        Returns:
            iterable of created repos
        """
        data = json.loads(content)
        repos = [cls(**r) for r in data]
        return repos

    def __eq__(self, other):
        return self.location == getattr(other, 'location', None)

    def __hash__(self):
        return hash(self.location)


class StubSource:
    """Abstract Base Class for Stub Sources"""

    def __init__(self, location, log=None):
        self.location = location
        _name = self.__class__.__name__
        self.log = log or Log.add_logger(_name)

    @contextmanager
    def ready(self, path=None, teardown=None):
        """Yields prepared Stub Source

        Allows StubSource subclasses to have a preperation
        method before providing a local path to itself.

        Args:
            path (str, optional): path to stub source.
                Defaults to location.
            teardown (func, optional): callback to execute on exit.
                Defaults to None.

        Yields:
            Resolved PathLike object to stub source
        """
        _path = path or self.location
        info_path = next(_path.rglob("info.json"), None)
        path = Path(info_path.parent) if info_path else _path
        yield path
        if teardown:
            teardown()

    def __str__(self):
        _name = self.__class__.__name__
        return f"<{_name}@{self.location}>"


class LocalStubSource(StubSource):
    """Stub Source Subclass for local locations

    Args:
        path (str): Path to Stub Source

    Returns:
        obj: Instance of LocalStubSource
    """

    def __init__(self, path, **kwargs):
        location = utils.ensure_existing_dir(path)
        return super().__init__(location, **kwargs)


class RemoteStubSource(StubSource):
    """Stub Source for remote locations

    Args:
        url (str): URL to Stub Source

    Returns:
        obj: Instance of RemoteStubSource
    """

    def __init__(self, name, **kwargs):
        location = StubRepo.resolve_package(name)
        return super().__init__(location, **kwargs)

    def _unpack_archive(self, file_bytes, path):
        """Unpack archive from bytes buffer

        Args:
            file_bytes (bytes): Byte array to extract from
                Must be from tarfile with gzip compression
            path (str): path to extract file to

        Returns:
            path: path extracted to
        """
        tar_bytes_obj = io.BytesIO(file_bytes)
        with tarfile.open(fileobj=tar_bytes_obj, mode="r:gz") as tar:
            tar.extractall(path.parent)
        return path

    def ready(self):
        """Retrieves and unpacks source

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
        outpath = tmp_path / filename
        _file_name = "".join(self.log.iter_formatted(f"$B[{filename}]"))
        content = utils.stream_download(
            self.location, desc=f"{self.log.get_service()} {_file_name}")
        source_path = self._unpack_archive(content, outpath)
        teardown = partial(shutil.rmtree, tmp_path)
        return super().ready(path=source_path, teardown=teardown)


def get_source(location, **kwargs):
    """Factory for StubSource Instance

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
