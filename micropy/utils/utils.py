# -*- coding: utf-8 -*-

"""
micropy.utils.utils
~~~~~~~~~~~~~~

This module contains generic utility helpers
used by MicropyCli
"""

from pathlib import Path

import requests
from requests.compat import urlparse
from requests.exceptions import ConnectionError, HTTPError, InvalidURL


def is_url(url):
    """Check if provided string is a url

    Args:
        url (str): url to check

    Returns:
        bool: True if arg url is a valid url
    """
    scheme = urlparse(str(url)).scheme
    return scheme in ('http', 'https',)


def ensure_valid_url(url):
    """Ensure a url is valid

    Args:
        url (str): URL to validate

    Raises:
        InvalidURL: URL is not a valid url
        ConnectionError: Failed to connect to url
        HTTPError: Reponse was not 200 <OK>

    Returns:
        str: valid url
    """
    if not is_url(url):
        raise InvalidURL(f"{url} is not a valid url!")
    try:
        resp = requests.head(url)
    except ConnectionError as e:
        raise e
    else:
        code = resp.status_code
        if not code == 200:
            msg = f"{url} ({code}) did not respond with OK <200>"
            raise HTTPError(msg)
    return url


def ensure_existing_dir(path):
    """Ensure path exists and is a directory

    If path does exist, it will be returned as
    a pathlib.PurePath object

    Args:
        path (str): path to validate and return

    Raises:
        NotADirectoryError: path does not exist
        NotADirectoryError: path is not a directory

    Returns:
        object: pathlib.PurePath object
    """
    _path = str(path)
    path = Path(_path).resolve()
    if not path.exists():
        raise NotADirectoryError(f"{_path} does not exist!")
    if not path.is_dir():
        raise NotADirectoryError(f"{_path} is not a directory!")
    return path
