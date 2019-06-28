# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from micropy import exceptions, stubs


def test_stub_validation(shared_datadir):
    """should pass validation"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    manager = stubs.StubManager()
    manager.validate(stub_path)


def test_bad_stub_validation(shared_datadir, mocker):
    """should fail validation"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    manager = stubs.StubManager()
    mock_validate = mocker.patch.object(stubs.stubs.utils, "Validator")
    mock_validate.return_value.validate.side_effect = [
        Exception, FileNotFoundError]
    with pytest.raises(exceptions.StubValidationError):
        manager.validate(stub_path)
    with pytest.raises(exceptions.StubValidationError):
        manager.validate(Path("/foobar/foo"))


def test_bad_stub(tmp_path):
    """should raise exception on invalid stub"""
    with pytest.raises(FileNotFoundError):
        stubs.stubs.Stub(tmp_path)


def test_valid_stub(shared_datadir):
    """should have all attributes"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    stub = stubs.stubs.Stub(stub_path)
    stub_2 = stubs.stubs.Stub(stub_path)
    assert stub == stub_2
    expect_device = {
        "nodename": "esp8266",
        "machine": "ESP module with ESP8266",
        "sysname": "esp8266",
        "release": "v1.9.4-8-ga9a3caad0 on 2018-05-11"
    }
    expect_repr = ("Stub(sysname=esp8266, firmware=micropython, version=1.9.4,"
                   f" path={stub_path})")
    assert stub.path.exists()
    assert stub.stubs.exists()
    assert stub.frozen.exists()
    assert stub.version == "1.9.4"
    assert stub.device == expect_device
    assert repr(stub) == expect_repr
    assert stub.firmware == "micropython"
    assert str(stub) == "esp8266-micropython-1.9.4"


def test_add_single_stub(shared_datadir, tmp_path):
    """should add a single stub"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    manager = stubs.StubManager()
    manager.add(stub_path, dest=tmp_path)
    assert len(manager) == 1
    assert stub_path.name in [d.name for d in tmp_path.iterdir()]


def test_add_stubs_from_dir(datadir, tmp_path):
    """should add all valid stubs in directory"""
    manager = stubs.StubManager()
    manager.add(datadir, dest=tmp_path)
    assert len(manager) == 1
    assert len(list(tmp_path.iterdir())) - 1 == len(manager)


def test_add_with_resource(datadir, tmp_path):
    """should not require dest kwarg"""
    manager = stubs.StubManager(resource=tmp_path)
    manager.add(datadir)
    assert len(manager) == 1
    # Subtract 1 cause tmp_path has datadir in it for some unrelated reason
    # as in, before adding stubs
    assert len(list(tmp_path.iterdir())) - 1 == len(manager)


def test_add_no_resource_no_dest(datadir):
    """should fail with typeerror"""
    manager = stubs.StubManager()
    with pytest.raises(TypeError):
        manager.add(datadir)


def test_loads_from_resource(datadir):
    """should load from resource if provided"""
    manager = stubs.StubManager(resource=datadir)
    assert len(manager) == len(list(datadir.iterdir())) - 1
