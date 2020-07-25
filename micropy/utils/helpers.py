# -*- coding: utf-8 -*-

"""
micropy.utils.helpers
~~~~~~~~~~~~~~

This module contains generic utility helpers
used by MicropyCli
"""

import inspect
import io
import subprocess as subproc
import sys
import tarfile
import xml.etree.ElementTree as ET
from datetime import timedelta
from pathlib import Path
import shutil

import requests
import requirements
from cachier import cachier
from packaging import version
from requests import exceptions as reqexc
from requests import utils as requtil
from tqdm import tqdm

import micropy
from micropy.lib.stubber.runOnPc import make_stub_files as stubgen

__all__ = ["is_url", "get_url_filename",
           "ensure_existing_dir", "ensure_valid_url",
           "is_downloadable", "is_existing_dir",
           "stream_download", "search_xml",
           "generate_stub", "get_package_meta",
           "extract_tarbytes", "iter_requirements",
           "create_dir_link", "is_dir_link",
           "is_update_available", "get_cached_data",
           "get_class_that_defined_method"]


def is_url(url):
    """Check if provided string is a url.

    Args:
        url (str): url to check

    Returns:
        bool: True if arg url is a valid url

    """
    scheme = requtil.urlparse(str(url)).scheme
    return scheme in ('http', 'https',)


@cachier(stale_after=timedelta(days=1))
def ensure_valid_url(url):
    """Ensure a url is valid.

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
    resp = requests.head(url, allow_redirects=True)
    resp.raise_for_status()
    return url


def ensure_existing_dir(path):
    """Ensure path exists and is a directory.

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
    path = _path.absolute()
    try:
        if not path.exists():
            raise NotADirectoryError(f"{_path} does not exist!")
        if not path.is_dir():
            raise NotADirectoryError(f"{_path} is not a directory!")
    except OSError:
        raise NotADirectoryError(f"{_path} is not a valid path!")
    return _path


def is_existing_dir(path):
    """Check if path is an existing directory.

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
    """Checks if the url can be downloaded from.

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
    """Parse filename from url.

    Args:
        url (str): url to parse

    Returns:
        str: filename of url

    """
    path = requtil.urlparse(url).path
    file_name = Path(path).name
    return file_name


def stream_download(url, **kwargs):
    """Stream download with tqdm progress bar.

    Args:
        url (str): url to file

    Returns:
        bytearray: bytearray of content

    """
    stream = requests.get(url, stream=True)
    content = bytearray()
    total_size = int(stream.headers.get('content-length', len(stream.content)))
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


@cachier(stale_after=timedelta(days=3))
def search_xml(url, node):
    """Search xml from url by node.

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


def generate_stub(path, log_func=None):
    """Create Stub from local .py file.

    Args:
        path (str): Path to file
        log_func (func, optional): Callback function for logging.
            Defaults to None.

    Returns:
        tuple: Tuple of file path and generated stub path.

    """
    mod_path = Path(stubgen.__file__).parent
    # Monkeypatch print to prevent or wrap output
    stubgen.print = lambda *args: None
    if log_func:
        stubgen.print = log_func
    cfg_path = (mod_path / 'make_stub_files.cfg').absolute()
    ctrl = stubgen.StandAloneMakeStubFile()
    ctrl.update_flag = True
    ctrl.config_fn = str(cfg_path)
    file_path = Path(path).absolute()
    stubbed_path = file_path.with_suffix('.pyi')
    ctrl.files = [file_path]
    ctrl.silent = True
    ctrl.scan_options()
    ctrl.run()
    files = (file_path, stubbed_path)
    return files


def iter_requirements(path):
    """Iterate requirements from a requirements.txt file.

    Args:
        path (str): path to file

    """
    req_path = Path(path).absolute()
    with req_path.open('r') as rfile:
        for req in requirements.parse(rfile):
            yield req


def get_package_meta(name, url):
    """Retrieve package metadata from PyPi.

    Args:
        name (str): Name of package with specs.
        url (str): Url to package.

    Returns:
        dict: Dictionary of Metadata

    """
    def _iter_compare(in_val, comp_to, operator):
        for t in comp_to:
            state = eval(f"in_val {operator} t")
            if state:
                yield t
    resp = requests.get(url)
    data = resp.json()
    pkg = next(requirements.parse(name))
    releases = data['releases']
    # Latest version
    spec_data = list(releases.items())[-1][1]
    if pkg.specs:
        spec_comp, spec_v = pkg.specs[0]
        spec_v = version.parse(spec_v)
        rel_versions = [version.parse(k) for k in releases.keys()]
        spec_key = str(next(_iter_compare(spec_v, rel_versions, spec_comp)))
        spec_data = releases[spec_key]
    # Find .tar.gz meta
    tar_meta = next((i for i in spec_data if ".tar.gz" in Path(i['url']).name))
    return tar_meta


def extract_tarbytes(file_bytes, path):
    """Extract tarfile as bytes.

    Args:
        file_bytes (bytearray): Bytes of file to extract
        path (str): Path to extract it to

    Returns:
        path: destination path

    """
    tar_bytes_obj = io.BytesIO(file_bytes)
    with tarfile.open(fileobj=tar_bytes_obj, mode="r:gz") as tar:
        tar.extractall(path)
    return path


def create_dir_link(source, target):
    """Creates a platform appropriate directory link.

    On POSIX systems it will create a symlink.
    On Windows it will fallback on a directory junction if needed

    Args:
        source (os.Pathlike): Path to create link at.
        target (os.Pathlike): Path to link to.

    Raises:
        OSError: Symlink Creation Failed
        OSError: Symlink and Directory Junction Fallback Failed

    """
    platform = sys.platform
    source = Path(source)
    target = Path(target)
    try:
        source.symlink_to(target, target_is_directory=True)
    except OSError as e:
        # Handle non-admin/non-dev windows links
        if not platform == "win32":
            # handles exFAT disk format (links not working)
            if e.errno == 38:
                shutil.copytree(
                    str(target.absolute()),
                    str(source.absolute()),
                    symlinks=False, ignore=None)
                return
            elif e.errno == 17:  # folder exists
                return
            else:
                raise e

        # Fall back to directory junction
        cmd = ["MKLINK", "/J", str(source.absolute()), str(target.absolute())]
        exit_code = subproc.call(
            cmd, shell=True, stdout=subproc.PIPE, stderr=subproc.PIPE)
        if exit_code:
            raise e


def is_dir_link(path):
    """Test if path is either a symlink or directory junction.

    Args:
        path (os.Pathlike): Path to test.

    Returns:
        bool: True if path is a type of link.

    """
    platform = sys.platform
    path = Path(path)
    if path.is_symlink():
        return True
    if platform == 'win32':
        # Test for Directory Junction
        resolved = str(path.resolve())
        if not str(path.absolute()) == resolved:
            return True
    return False


def is_update_available():
    """Check if micropy-cli update is available.

    Returns:
        bool: True if update available, else False.

    """
    url = f"https://pypi.org/pypi/micropy-cli/json"
    data = get_cached_data(url)
    versions = [k for k in data['releases'].keys() if 'rc' not in k]
    if versions:
        latest = version.parse(versions[-1])
        cur_version = version.parse(micropy.__version__)
        if cur_version < latest:
            return str(latest)
    return False


@cachier(stale_after=timedelta(days=3))
def get_cached_data(url):
    """Wrap requests with a short cache."""
    source_data = requests.get(url).json()
    return source_data


def get_class_that_defined_method(meth):
    """Determines Class that defined a given method.

    See - https://stackoverflow.com/a/25959545

    Args:
        meth (Callable): Method to determine class from

    Returns:
        Callable: Class that defined method

    """
    if inspect.ismethod(meth):
        for cls in inspect.getmro(meth.__self__.__class__):
            if cls.__dict__.get(meth.__name__) is meth:
                return cls
        meth = meth.__func__  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)  # handle special descriptor objects
