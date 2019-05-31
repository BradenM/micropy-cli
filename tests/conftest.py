# -*- coding: utf-8 -*-
""" Common Pytest Fixtures"""

import pytest
from pyfakefs import *
import linecache
import tokenize
from pyfakefs.fake_filesystem_unittest import Patcher
from micropy import micropy, project
import os.path
from pathlib import Path


@pytest.fixture
def fs_micropy():
    patcher = Patcher(modules_to_reload=[micropy, project])
    patcher.setUp()
    linecache.open = patcher.original_open
    tokenize._builtin_open = patcher.original_open
    yield patcher.fs
    patcher.tearDown()


@pytest.fixture
def mock_micropy(fs_micropy):
    tmp_dir = Path(os.getenv('HOME'))
    fs_micropy.create_dir(tmp_dir)
    mp = micropy.MicroPy()
    fs_micropy.add_real_directory(mp.TEMPLATE)
    return mp
