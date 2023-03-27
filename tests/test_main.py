import micropy.exceptions as exc
import pytest
from micropy import data, main


def test_setup(mock_micropy_path):
    """Tests MicroPy Initial Setup"""
    expect_mp_dir = mock_micropy_path
    expect_stubs_dir = mock_micropy_path / "stubs"
    config = main.MicroPyOptions(root_dir=mock_micropy_path)
    mp = main.MicroPy(options=config)
    assert expect_mp_dir.exists()
    assert expect_stubs_dir.exists()
    # Test after inital setup
    mp_ = main.MicroPy(options=config)
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


def test_stub_error():
    with pytest.raises(exc.StubError):
        raise exc.StubError(None)


def test_resolve_project(mocker, mock_micropy):
    mock_proj = mocker.patch.object(main, "Project").return_value
    mock_proj.exists = False
    assert not mock_micropy.resolve_project(".").exists
    mock_proj.exists = True
    assert mock_micropy.resolve_project(".")
