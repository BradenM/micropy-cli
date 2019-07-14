# -*- coding: utf-8 -*-

"""
micropy.utils.helpers
~~~~~~~~~~~~~~

This module contains generic utility helpers
used by MicropyCli
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import requests
from requests import exceptions as reqexc
from requests import utils as requtil
from tqdm import tqdm

__all__ = ["is_url", "get_url_filename",
           "ensure_existing_dir", "ensure_valid_url",
           "is_downloadable", "is_existing_dir",
           "stream_download", "search_xml"]


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
    _path = Path(path)
    path = _path.resolve()
    if not path.exists():
        raise NotADirectoryError(f"{_path} does not exist!")
    if not path.is_dir():
        raise NotADirectoryError(f"{_path} is not a directory!")
    return _path


def is_existing_dir(path):
    """Check if path is an existing directory

    Args:
        path (str): path to check

    Returns:
        bool: True if path exists and is a directory
    """
    try:
        ensure_existing_dir(path)
    except NotADirectoryError:
        return False
    else:
        return True


def is_downloadable(url):
    """Checks if the url can be downloaded from

    Args:
        url (str): url to check

    Returns:
        bool: True if contains a downloadable resource
    """
    try:
        ensure_valid_url(url)
    except Exception:
        return False
    headers = requests.head(url).headers
    content_type = headers.get("content-type").lower()
    ctype = content_type.split("/")
    if any(t in ('text', 'html', ) for t in ctype):
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


def stream_download(url, **kwargs):
    """Stream download with tqdm progress bar

    Args:
        url (str): url to file

    Returns:
        bytearray: bytearray of content
    """
    stream = requests.get(url, stream=True)
    content = bytearray()
    total_size = int(stream.headers.get('content-length'))
    block_size = 32*1024
    bar_format = "{l_bar}{bar}| [{n_fmt}/{total_fmt} @ {rate_fmt}]"
    tqdm_kwargs = {
        "unit_scale": True,
        "unit_divisor": 1024,
        "smoothing": 0.1,
        "bar_format": bar_format,
    }
    tqdm_kwargs.update(kwargs)
    with tqdm(total=total_size, unit='B', **tqdm_kwargs) as pbar:
        for block in stream.iter_content(block_size):
            pbar.update(len(block))
            content.extend(block)
    return content


def search_xml(url, node):
    """Search xml from url by node

    Args:
        url (str): url to xml
        node (str): node to search for

    Returns:
        [str]: matching nodes
    """
    resp = requests.get(url)
    xml = resp.content.decode("UTF-8")
    root = ET.fromstring(xml)
    root_ns = root.tag[1:root.tag.find('}')]
    namespace = {'ns': root_ns}
    _results = root.findall(f"./*/ns:{node}", namespace)
    results = [k.text for k in _results]
    return results
