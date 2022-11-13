"""
micropy.utils
~~~~~~~~~~~~~~

This module provides utility functions that are used within
MicropyCli.
"""

from .decorators import lazy_property
from .helpers import (
    create_dir_link,
    ensure_existing_dir,
    ensure_valid_url,
    extract_tarbytes,
    get_cached_data,
    get_class_that_defined_method,
    get_package_meta,
    get_url_filename,
    is_dir_link,
    is_downloadable,
    is_existing_dir,
    is_update_available,
    is_url,
    iter_requirements,
    search_xml,
    stream_download,
)
from .stub import generate_stub
from .validate import Validator
