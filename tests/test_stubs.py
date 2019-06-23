

import pytest

from micropy import exceptions, stubs


def test_bad_stub(tmp_path):
    """should raise exception on invalid stub"""
    with pytest.raises(FileNotFoundError):
        stubs.Stub(tmp_path)


def test_valid_stub(shared_datadir):
    """should have all attributes"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    stub = stubs.stubs.Stub(stub_path)
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
    assert stub.name == "esp8266@v1.9.4-8-ga9a3caad0 on 2018-05-11"
    assert expect_module in stub.modules
    assert str(stub) == "esp8266@v1.9.4-8-ga9a3caad0 on 2018-05-11"


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


def test_add_with_resource(datadir, tmp_path):
    """should not require dest kwarg"""
    manager = stubs.StubManager(resource=tmp_path)
    manager.add(datadir)
    assert len(manager) == 2
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


import pytest

from micropy import exceptions, stubs


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
    stub = stubs.stubs.Stub(stub_path)
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
    assert stub.name == "esp8266@v1.9.4-8-ga9a3caad0 on 2018-05-11"
    assert expect_module in stub.modules
    assert str(stub) == "esp8266@v1.9.4-8-ga9a3caad0 on 2018-05-11"


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


def test_add_with_resource(datadir, tmp_path):
    """should not require dest kwarg"""
    manager = stubs.StubManager(resource=tmp_path)
    manager.add(datadir)
    assert len(manager) == 2
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
