# -*- coding: utf-8 -*-

import pytest
from micropy import micropy
from pathlib import Path
import os
import requests


def test_setup(fs_micropy):
    """Tests MicroPy Initial Setup"""
    tmp_dir = Path(os.getenv('HOME'))
    fs_micropy.create_dir(tmp_dir)
    expect_mp_dir = tmp_dir / '.micropy'
    mp = micropy.MicroPy()
    assert expect_mp_dir.exists()
    assert mp.FILES == expect_mp_dir


def test_add_stub(fs_micropy, mock_micropy):
    """Test Adding Stub"""
    stub_path = Path('/foo/bar/foobar_stub')
    fs_micropy.create_dir(stub_path)
    stub = mock_micropy.add_stub(stub_path)
    assert stub in mock_micropy.STUBS
    assert stub.path in mock_micropy.STUB_DIR.iterdir()
    assert stub.path.exists()



