# -*- coding: utf-8 -*-
""" Common Pytest Fixtures"""

from pathlib import Path

import pytest
import questionary

import micropy


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


@pytest.fixture
def mock_micropy_path(monkeypatch, tmp_path):
    path = tmp_path / '.micropy'
    stub_path = path / 'stubs'
    log_path = path / 'micropy.log'
    monkeypatch.setattr(micropy.logger.ServiceLog, 'LOG_FILE', log_path)
    monkeypatch.setattr(micropy.main.MicroPy, 'FILES', path)
    monkeypatch.setattr(micropy.main.MicroPy, 'STUB_DIR', stub_path)
    return path


@pytest.fixture
def mock_micropy(mock_micropy_path):
    mp = micropy.main.MicroPy()
    return mp


@pytest.fixture
def mock_cwd(monkeypatch, tmp_path):
    """Mock Path.cwd"""
    def _mock_cwd():
        return tmp_path

    def _mock_resolve(self, **kwargs):
        return tmp_path / self
    monkeypatch.setattr(Path, 'cwd', _mock_cwd)
    monkeypatch.setattr(Path, 'resolve', _mock_resolve)
    return tmp_path


@pytest.fixture(scope="session")
def test_urls():
    def test_headers(type): return {
        "content-type": type
    }
    return {
        "valid": "http://www.google.com",
        "valid_https": "https://www.google.com",
        "invalid": "/foobar/bar/foo",
        "invalid_file": "file:///foobar/bar/foo",
        "bad_resp": "http://www.google.com/XYZ/ABC/BADRESP",
        "download": "https://www.somewebsite.com/archive_test_stub.tar.gz",
        "headers": {
            "can_download": test_headers("application/gzip"),
            "not_download": test_headers("text/plain")
        }
    }


@pytest.fixture
def mock_mp_stubs(mock_micropy, mocker, shared_datadir):
    mock_micropy.STUBS.add((shared_datadir / 'fware_test_stub'))
    mock_micropy.STUBS.add((shared_datadir / 'esp8266_test_stub'))
    mock_micropy.STUBS.add((shared_datadir / 'esp32_test_stub'))
    return mock_micropy


@pytest.yield_fixture
def test_archive(shared_datadir):
    archive = shared_datadir / 'archive_test_stub.tar.gz'
    file_obj = archive.open('rb')
    file_bytes = file_obj.read()
    yield file_bytes
    file_obj.close()
