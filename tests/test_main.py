from shutil import copytree, rmtree

import micropy.exceptions as exc
import pytest
from micropy import data, main
from micropy.stubs import StubManager, stubs
from pytest_mock import MockFixture


def test_setup(mock_micropy_path):
    """Tests MicroPy Initial Setup"""
    expect_mp_dir = mock_micropy_path
    expect_stubs_dir = mock_micropy_path / "stubs"
    mp = main.MicroPy()
    assert expect_mp_dir.exists()
    assert expect_stubs_dir.exists()
    # Test after inital setup
    mp_ = main.MicroPy()
    assert len(mp_.stubs) == len(mp.stubs)


def test_add_stub(mock_micropy, shared_datadir):
    """Test Adding Valid Stub"""
    fware_path = shared_datadir / "fware_test_stub"
    stub_path = shared_datadir / "esp8266_test_stub"
    stubs = mock_micropy.stubs
    fware_stub = stubs.add(fware_path, data.STUB_DIR)
    stub = stubs.add(stub_path, data.STUB_DIR)
    assert stub in list(mock_micropy.stubs)
    assert stub.path in data.STUB_DIR.iterdir()
    assert stub.path.exists()
    assert fware_stub in list(mock_micropy.stubs._firmware)


def test_create_stub__connect_error(mock_micropy, mocker, shared_datadir, tmp_path):
    mock_pyb = mocker.patch("micropy.main.PyDevice")
    mock_pyb.side_effect = [SystemExit, exc.PyDeviceError]
    mp = mock_micropy
    assert mp.create_stubs("/dev/PORT") is None
    assert mp.create_stubs("/dev/PORT") is None


def test_create_stub(mock_micropy, mocker: MockFixture, shared_datadir, tmp_path):
    """should create and add stubs"""
    mock_micropy.stubs.add(shared_datadir / "fware_test_stub")
    tmp_stub_path = tmp_path / "createtest"
    tmp_stub_path.mkdir()
    copytree(str(shared_datadir / "stubber_test_stub"), str(tmp_stub_path / "stubber_test_stub"))
    mock_tmpdir = mocker.patch("micropy.main.tempfile.TemporaryDirectory")
    mock_tmpdir.return_value.__enter__.return_value = tmp_stub_path
    mock_pyb = mocker.patch("micropy.main.PyDevice")
    mp = mock_micropy
    mocker.spy(StubManager, "add")
    mock_pyb.return_value.run_script.side_effect = [Exception, mocker.ANY, mocker.ANY]
    with pytest.raises(Exception):
        stub = mp.create_stubs("/dev/PORT")
    stub = mp.create_stubs("/dev/PORT")
    mp.stubs.add.assert_any_call(mocker.ANY, tmp_stub_path / "esp32-1.11.0")
    rmtree(tmp_stub_path / "esp32-1.11.0")
    assert isinstance(stub, stubs.DeviceStub)


def test_stub_error():
    with pytest.raises(exc.StubError):
        raise exc.StubError(None)


def test_resolve_project(mocker, mock_micropy):
    mock_proj = mocker.patch.object(main, "Project").return_value
    mock_proj.exists = False
    assert not mock_micropy.resolve_project(".").exists
    mock_proj.exists = True
    assert mock_micropy.resolve_project(".")
