# -*- coding: utf-8 -*-

import shutil
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
    stub_type = manager._get_stubtype(device_stub)
    assert stub_type == stubs.stubs.DeviceStub
    stub_type = manager._get_stubtype(fware_stub)
    assert stub_type == stubs.stubs.FirmwareStub
    with pytest.raises(exceptions.StubError):
        manager._get_stubtype(Path('/foobar/foo'))
    with pytest.raises(exceptions.StubValidationError):
        manager._get_stubtype(invalid_stub)


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


def test_add_with_resource(datadir, mock_fware, tmp_path, mocker):
    """should not require dest kwarg"""
    resource = tmp_path / 'tmp_resource'
    resource.mkdir()
    load_spy = mocker.spy(stubs.StubManager, '_load')
    manager = stubs.StubManager(resource=resource)
    manager.add(datadir)
    assert len(manager) == 2
    assert "esp8266_test_stub" in [p.name for p in resource.iterdir()]
    assert load_spy.call_count == 5
    # Should not add any new stubs
    assert manager.add(datadir)
    assert load_spy.call_count == 5
    # Should force load
    assert manager.add(datadir, force=True)
    assert load_spy.call_count == 10


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


def test_stub_resolve_link(mock_mp_stubs, tmp_path):
    """should create DeviceStub from symlink"""
    stub = list(mock_mp_stubs.stubs)[0]
    link_path = tmp_path / 'stub_symlink'
    linked_stub = stubs.stubs.DeviceStub.resolve_link(stub, link_path)
    assert stub == linked_stub
    assert stub.path != linked_stub.path
    assert linked_stub.path.is_symlink()
    assert linked_stub.path.resolve() == stub.path


def test_manager_resolve_subresource(mock_mp_stubs, tmp_path):
    """should create StubManager from subresource symlinks"""
    test_stubs = list(mock_mp_stubs.stubs)[:2]
    subresource = tmp_path / 'stub_subresource'
    subresource.mkdir()
    manager = mock_mp_stubs.stubs.resolve_subresource(test_stubs, subresource)
    linked_stub = list(manager)[0]
    assert linked_stub.path.is_symlink()
    assert linked_stub in list(mock_mp_stubs.stubs)


def test_load_firmware_first(mocker, tmp_path, shared_datadir):
    """should always load firmware first"""
    mock_manager = mocker.patch.object(stubs.StubManager, "_load")
    mock_iterdir = mocker.patch.object(stubs.stubs.Path, 'iterdir')
    # mock_mgr = mock_manager.return_value
    tmp_path = tmp_path / 'fware_first_test'
    tmp_resource = tmp_path / 'tmp_resource'
    tmp_resource.mkdir(parents=True)
    test_stub = shared_datadir / 'esp32_test_stub'
    test_fware = shared_datadir / 'fware_test_stub'
    # Ensure Firmware loads first, regardless of how Path.iterdir() orders it
    shutil.copytree(test_stub, (tmp_path / '99_esp32_test_stub'))
    shutil.copytree(test_fware, (tmp_path / '00_fware_test_stub'))
    mock_iterdir.return_value = (test_stub, test_fware)
    manager = stubs.StubManager(resource=tmp_resource)
    manager.load_from(tmp_path)
    # Get First call args
    fargs, _ = mock_manager.call_args_list[0]
    assert fargs[0].location == test_fware


def test_iter_by_firm_stubs(mocker):
    """should iter stubs by firmware"""
    firm_stub = mocker.MagicMock()
    dev_stub = mocker.MagicMock()
    dev_stub.firmware = firm_stub
    unk_stub = mocker.MagicMock()
    unk_stub.firmware = None
    manager = stubs.StubManager()
    manager._loaded = set([firm_stub, dev_stub, unk_stub])
    manager._firmware = set([firm_stub])
    stub_iter = list(manager.iter_by_firmware())
    assert stub_iter == [(firm_stub, [dev_stub]), ('Unknown', [unk_stub])]
