# -*- coding: utf-8 -*-

import pytest
from micropy import stubs, exceptions


def test_stubs_load(mock_micropy):
    """should load stubs"""
    path = mock_micropy.STUBS_DIR
    manager = stubs.StubManager()
    manager.load_from(path)
    assert len(path.iterdir()) == len(manager.loaded)


def test_stub_validation(shared_datadir):
    """should pass validation"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    manager = stubs.StubManager()
    manager.validate(stub_path)


def test_bad_stub_validation(shared_datadir):
    """should fail validation"""
    stub_path = shared_datadir / 'esp8266_invalid_stub'
    manager = stubs.StubManager()
    with pytest.raises(exceptions.StubValidationError):
        manager.validate(stub_path)


def test_bad_stub(tmp_path):
    """should raise exception on invalid stub"""
    with pytest.raises(FileNotFoundError):
        stubs.Stub(tmp_path)


def test_valid_stub(shared_datadir):
    """should have all attributes"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    stub = stubs.Stub(stub_path)
    expect_module = {
        "file": "/stubs/esp8266_test_stub/micropython.py",
        "module": "micropython"
    }
    assert stub.path.exists()
    assert stub.nodename == "esp8266"
    assert stub.release == "2.2.0-dev(9422289)"
    assert stub.version == "v1.9.4-8-ga9a3caad0 on 2018-05-11"
    assert stub.machine == "ESP module with ESP8266"
    assert stub.sysname == "esp8266"
    assert expect_module in stub.modules
    assert str(stub) == "esp8266@v1.9.4-8-ga9a3caad0 on 2018-05-11"
