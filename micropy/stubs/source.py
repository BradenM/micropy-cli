# -*- coding: utf-8 -*-

"""
micropy.stubs.source
~~~~~~~~~~~~~~

This module contains abstractions for handling stub sources
and their location.
"""


from micropy import utils
from micropy.logger import Log


class StubSource:
    """Stub Source Base Class"""

    def __init__(self, location):
        self.location = location
        _name = self.__class__.__name__
        self.log = Log.add_logger(_name)


class LocalStubSource(StubSource):
    """Stub Source Subclass for local locations

    Args:
        path (str): Path to Stub Source

    Returns:
        obj: Instance of LocalStubSource
    """

    def __init__(self, path):
        location = utils.ensure_existing_dir(path)
        return super().__init__(location)


class RemoteStubSource(StubSource):
    """Stub Source for remote locations

    Args:
        url (str): URL to Stub Source

    Returns:
        obj: Instance of RemoteStubSource
    """

    def __init__(self, url):
        location = utils.ensure_valid_url(url)
        return super().__init__(location)


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
