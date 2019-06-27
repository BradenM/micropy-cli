# -*- coding: utf-8 -*-

"""
micropy.utils.helpers
~~~~~~~~~~~~~~

This module contains generic utility helpers
used by MicropyCli
"""

from pathlib import Path

import requests
from requests import exceptions as reqexc
from requests import utils as requtil

__all__ = ["is_url", "get_url_filename",
           "ensure_existing_dir", "ensure_valid_url",
           "is_downloadable"]


def is_url(url):
    """Check if provided string is a url

    Args:
        url (str): url to check

    Returns:
        bool: True if arg url is a valid url
    """
    scheme = requtil.urlparse(str(url)).scheme
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
        raise reqexc.InvalidURL(f"{url} is not a valid url!")
    try:
        resp = requests.head(url)
    except reqexc.ConnectionError as e:
        raise e
    else:
        resp.raise_for_status()
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


def is_downloadable(url):
    """Checks if the url can be downloaded from

    Args:
        url (str): url to check

    Returns:
        bool: True if contains a downloadable resource
    """
    headers = requests.head(url).headers
    content_type = headers.get("content-type").lower()
    ctype = content_type.split("/")
    if any(t in ('text', 'html',) for t in ctype):
        return False
    return True


def get_url_filename(url):
    """Parse filename from url

    Args:
        url (str): url to parse

    Returns:
        str: filename of url
    """
    path = requtil.urlparse(url).path
    file_name = Path(path).name
    return file_name
