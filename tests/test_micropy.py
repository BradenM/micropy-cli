# -*- coding: utf-8 -*-

import pytest
from pyfakefs import *
import linecache
import tokenize
from pyfakefs.fake_filesystem_unittest import Patcher
from micropy import micropy
import os.path
from pathlib import Path


@pytest.fixture
def fs_reload_micropy():
    patcher = Patcher(modules_to_reload=[micropy])
    patcher.setUp()
    linecache.open = patcher.original_open
    tokenize._builtin_open = patcher.original_open
    yield patcher.fs
    patcher.tearDown()


def test_setup(fs_reload_micropy):
    """Tests MicroPy Initial Setup"""
    tmp_dir = Path(os.getenv('HOME'))
    fs_reload_micropy.create_dir(tmp_dir)
    expect_mp_dir = tmp_dir / '.micropy'
    mp = micropy.MicroPy()
    assert expect_mp_dir.exists()
    assert mp.FILES == expect_mp_dir
