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
    with pytest.raises(FileNotFoundError):
        manager.validate(Path("/foobar/foo"))


def test_bad_stub(tmp_path):
    """should raise exception on invalid stub"""
    with pytest.raises(FileNotFoundError):
        stubs.stubs.DeviceStub(tmp_path)


def test_valid_stub(shared_datadir):
    """should have all attributes"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    stub = stubs.stubs.DeviceStub(stub_path)
    stub_2 = stubs.stubs.DeviceStub(stub_path)
    assert stub == stub_2
    expect_fware = {
        "machine": "ESP module with ESP8266",
        "firmware": "esp8266 v1.9.4",
        "nodename": "esp8266",
        "version": "1.9.4",
        "release": "2.2.0-dev(9422289)",
        "sysname": "esp8266",
        "name": "micropython"
    }
    expect_repr = ("DeviceStub(sysname=esp8266, firmware=micropython,"
                   f" version=1.9.4, path={stub_path})")
    assert stub.path.exists()
    assert stub.stubs.exists()
    assert stub.frozen.exists()
    assert stub.version == "1.9.4"
    assert stub.firmware == expect_fware
    assert repr(stub) == expect_repr
    assert stub.firmware_name == "micropython"
    assert str(stub) == "esp8266-micropython-1.9.4"
    del stub.firmware['name']
    assert stub.firmware_name == "esp8266 v1.9.4"


def test_valid_fware_stub(shared_datadir):
    stub_path = shared_datadir / 'fware_test_stub'
    stub = stubs.stubs.FirmwareStub(stub_path)
    assert str(stub) == "MicroPython Official"
    assert stub.frozen.exists()
    assert repr(
        stub) == ("FirmwareStub(firmware=micropython,"
                  " repo=micropython/micropython)")


def test_resolve_stub(shared_datadir):
    """should resolve correct stub type"""
    device_stub = shared_datadir / 'esp8266_test_stub'
    fware_stub = shared_datadir / 'fware_test_stub'
    invalid_stub = shared_datadir / 'esp8266_invalid_stub'
    manager = stubs.StubManager()
    stub_type = manager.resolve_stub(device_stub)
    assert stub_type == stubs.stubs.DeviceStub
    stub_type = manager.resolve_stub(fware_stub)
    assert stub_type == stubs.stubs.FirmwareStub
    with pytest.raises(FileNotFoundError):
        manager.resolve_stub(Path('/foobar/foo'))
    with pytest.raises(exceptions.StubValidationError):
        manager.resolve_stub(invalid_stub)


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


def test_name_property(shared_datadir):
    """should raise error if name is not overriden"""
    test_stub = shared_datadir / 'esp8266_test_stub'

    class ErrorStub(stubs.stubs.Stub):
        def __init__(self, path, copy_to=None, **kwargs):
            return super().__init__(path, copy_to=copy_to, **kwargs)
    with pytest.raises(NotImplementedError):
        x = ErrorStub(test_stub)
        x.name
