# -*- coding: utf-8 -*-

import pytest
from micropy import micropy
from pathlib import Path
import os


def test_setup(fs_reload_micropy):
    """Tests MicroPy Initial Setup"""
    tmp_dir = Path(os.getenv('HOME'))
    fs_reload_micropy.create_dir(tmp_dir)
    expect_mp_dir = tmp_dir / '.micropy'
    mp = micropy.MicroPy()
    assert expect_mp_dir.exists()
    assert mp.FILES == expect_mp_dir
