# -*- coding: utf-8 -*-

import pytest
from pathlib import Path
from micropy.stubs import Stub


def test_stub_init(mock_micropy, tmp_path):
    """Tests Stub Init"""
    print(tmp_path)
    mock_stub_name = Stub.clean_stub_name(tmp_path)
    stub = Stub.create_from_path(mock_micropy.STUB_DIR, tmp_path)
    assert stub.name == mock_stub_name.name
    assert stub.path.exists()
    assert stub.path in mock_micropy.STUB_DIR.iterdir()


def test_stub_clean(tmp_path):
    """Tests Stub Name Cleaning"""
    mock_stub = tmp_path / 'some-stub(1234)'
    clean_stub = Stub.clean_stub_name(mock_stub)
    assert clean_stub.name == 'some-stub'


