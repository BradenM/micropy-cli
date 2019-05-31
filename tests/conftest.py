# -*- coding: utf-8 -*-
""" Common Pytest Fixtures"""

import pytest
import linecache
import tokenize
import pyfakefs
from pyfakefs.fake_filesystem_unittest import Patcher
from micropy import micropy, project
import os.path
from pathlib import Path
import questionary


@pytest.fixture
def fs_micropy():
    pyfakefs.fake_filesystem.set_uid(0)
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


@pytest.fixture
def mock_prompt(monkeypatch):
    def mock_prompt(*args, **kwargs):
        class prompt_mock:
            def __init__(self, *args, **kwargs):
                return None

            def ask(self):
                return ['stub']
        return prompt_mock(*args, **kwargs)
    monkeypatch.setattr(questionary, 'checkbox', mock_prompt)
