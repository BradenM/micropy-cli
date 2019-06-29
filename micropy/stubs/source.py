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

import requests
from micropy import utils
from micropy.logger import Log


class StubRepo:
    """Represents a remote repository for stubs

    Args:
        name (str): Repo Name
        location (str): Valid url
        ref (str): path to repo definition file
    """

    def __init__(self, name, location, ref):
        self.packages = set()
        self.name = name
        self.location = utils.ensure_valid_url(location)
        self.ref = ref
        self.synced = False

    def _load(self, content):
        """Loads packages from def file

        Args:
            content (str or bytes): json data to load

        Returns:
            set of available packages
        """
        data = json.loads(content)
        packages = data['packages']
        for pkg in packages:
            location = pkg.pop("url")
            source = get_source(location, **pkg)
            self.packages.add(source)
        return self.packages

    def fetch(self):
        """Fetch repo info

        Returns:
            set: available packages
        """
        if self.synced:
            return self.packages
        url = f"{self.location}/{self.ref}"
        data = requests.get(url)
        self.synced = True
        return self._load(data.content)

    @classmethod
    def from_json(cls, content):
        """Create StubRepo Instances from JSON file

        Args:
            file_obj (str or bytes): json content

        Returns:
            iterable of created repos
        """
        data = json.loads(content)
        repos = iter(cls(**r) for r in data)
        return repos


class StubSource:
    """Abstract Base Class for Stub Sources"""

    def __init__(self, location, **kwargs):
        self.location = location
        self.firmware = kwargs.get("firmware", "Unknown")
        self.device = kwargs.get("device", "Unknown")
        self.version = kwargs.get("version", "Unknown")
        _name = self.__class__.__name__
        self.log = Log.add_logger(_name)

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
        path = Path(_path).resolve()
        yield path
        if teardown:
            teardown()

    def __str__(self):
        return f"{self.device}-{self.firmware}-{self.version}"


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

    def __init__(self, url, **kwargs):
        location = utils.ensure_valid_url(url)
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
            tar.extractall(path)
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
        resp = requests.get(self.location)
        source_path = self._unpack_archive(resp.content, outpath)
        teardown = partial(shutil.rmtree, tmp_path)
        return super().ready(path=source_path, teardown=teardown)


def get_source(location, **kwargs):
    """Factory for StubSource Instance

    Args:
        location (str): PathLike object or valid URL

    Returns:
        obj: Either Local or Remote StubSource Instance
    """
    if utils.is_url(location):
        return RemoteStubSource(location, **kwargs)
    return LocalStubSource(location, **kwargs)
