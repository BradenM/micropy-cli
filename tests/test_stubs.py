# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from micropy import exceptions, stubs


@pytest.fixture
def mock_fware(mocker, shared_datadir):
    def mock_ready(self, *args, **kwargs):
        fware_stub = shared_datadir / 'fware_test_stub'
        return super().ready(path=fware_stub)
    mock_remote = mocker.patch.object(
        stubs.source, "RemoteStubSource").return_value
    mock_remote.ready.return_value = mock_ready


def test_stub_validation(shared_datadir):
    """should pass validation"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    manager = stubs.StubManager()
    manager.validate(stub_path)
    assert manager.is_valid(stub_path)
    assert not manager.is_valid(Path('/foobar/bar'))


def test_bad_stub_validation(shared_datadir, mocker):
    """should fail validation"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    manager = stubs.StubManager()
    mock_validate = mocker.patch.object(stubs.stubs.utils, "Validator")
    mock_validate.return_value.validate.side_effect = [
        Exception, FileNotFoundError]
    with pytest.raises(exceptions.StubValidationError):
        manager.validate(stub_path)
    with pytest.raises(exceptions.StubError):
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
    fware = stubs.stubs.FirmwareStub((shared_datadir / 'fware_test_stub'))
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
    assert stub.firm_info == expect_fware
    assert repr(stub) == expect_repr
    assert str(stub) == "esp8266-1.9.4"
    assert stub.firmware_name == "micropython"
    del stub.firm_info['name']
    assert stub.firmware_name == "esp8266 v1.9.4"
    stub.firmware = fware
    assert stub.firmware_name == "micropython"
    assert str(stub) == "esp8266-micropython-1.9.4"


def test_valid_fware_stub(shared_datadir):
    stub_path = shared_datadir / 'fware_test_stub'
    stub = stubs.stubs.FirmwareStub(stub_path)
    assert str(stub) == "micropython"
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
    with pytest.raises(exceptions.StubError):
        manager.resolve_stub(Path('/foobar/foo'))
    with pytest.raises(exceptions.StubValidationError):
        manager.resolve_stub(invalid_stub)


def test_resolve_firmware(tmp_path, shared_datadir):
    """should resolve firmware"""
    device_stub = shared_datadir / 'esp8266_test_stub'
    fware_stub_path = shared_datadir / 'fware_test_stub'
    manager = stubs.StubManager(resource=tmp_path)
    fware_stub = manager.add(fware_stub_path)
    dev_stub = stubs.stubs.DeviceStub(device_stub)
    resolved = manager.resolve_firmware(dev_stub)
    assert fware_stub == resolved


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
    assert len(manager) == 2
    assert len(list(tmp_path.iterdir())) - 1 == len(manager)
    assert manager._should_recurse(datadir)
    with pytest.raises(exceptions.StubError):
        empty_path = tmp_path / 'empty'
        empty_path.mkdir()
        manager._should_recurse(empty_path)


def test_add_with_resource(datadir, mock_fware, tmp_path):
    """should not require dest kwarg"""
    manager = stubs.StubManager(resource=tmp_path)
    manager.add(datadir)
    assert len(manager) == 2
    assert "esp8266_test_stub" in [p.name for p in tmp_path.iterdir()]


def test_add_no_resource_no_dest(datadir, mock_fware):
    """should fail with typeerror"""
    manager = stubs.StubManager()
    with pytest.raises(TypeError):
        manager.add(datadir)


def test_loads_from_resource(datadir, mock_fware):
    """should load from resource if provided"""
    manager = stubs.StubManager(resource=datadir)
    assert len(manager) == 2


def test_name_property(shared_datadir):
    """should raise error if name is not overriden"""
    test_stub = shared_datadir / 'esp8266_test_stub'

    class ErrorStub(stubs.stubs.Stub):
        def __init__(self, path, copy_to=None, **kwargs):
            return super().__init__(path, copy_to=copy_to, **kwargs)
    with pytest.raises(NotImplementedError):
        x = ErrorStub(test_stub)
        x.name


def test_stub_search(mocker, test_urls, shared_datadir, tmp_path, test_repo):
    test_fware = shared_datadir / 'fware_test_stub'
    test_stub = shared_datadir / 'esp8266_test_stub'
    mock_results = [
        "packages/esp8266-micropython-1.9.4.tar.gz",
        "packages/esp32-micropython-1.11.0.tar.gz"
    ]
    mock_search = mocker.patch.object(stubs.source.utils, 'search_xml')
    mock_search.return_value = mock_results
    tmp_path = tmp_path / 'foobar'
    tmp_path.mkdir()
    manager = stubs.StubManager(resource=tmp_path, repos=[test_repo])
    manager.add(test_fware)
    print(manager._firmware)
    print(list(manager))
    manager.add(test_stub)
    results = manager.search_remote("esp8266")
    assert len(results) == 1
    res = results[0]
    assert res[0] == "esp8266-micropython-1.9.4"
    assert res[1]
    results = manager.search_remote("esp32")
    res = results[0]
    assert res[0] == "esp32-micropython-1.11.0"
    assert not res[1]
