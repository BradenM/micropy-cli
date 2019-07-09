# -*- coding: utf-8 -*-

from pathlib import Path
from shutil import copytree

from micropy import main
from micropy.stubs import stubs


def test_setup(mock_micropy_path):
    """Tests MicroPy Initial Setup"""
    expect_mp_dir = mock_micropy_path
    expect_stubs_dir = mock_micropy_path / 'stubs'
    mp = main.MicroPy()
    print("MP FILES:", mp.FILES)
    print("MP Content:", list(mp.FILES.iterdir()))
    assert expect_mp_dir.exists()
    assert expect_stubs_dir.exists()
    # Test after inital setup
    mp_ = main.MicroPy()
    assert len(mp_.STUBS) == len(mp.STUBS)


def test_add_stub(mock_micropy, shared_datadir):
    """Test Adding Valid Stub"""
    stub_path = shared_datadir / 'esp8266_test_stub'
    stubs = mock_micropy.STUBS
    stub = stubs.add(stub_path, mock_micropy.STUB_DIR)
    assert stub in list(mock_micropy.STUBS)
    assert stub.path in mock_micropy.STUB_DIR.iterdir()
    assert stub.path.exists()


def test_create_stub(mock_micropy_path, mocker, shared_datadir, tmp_path):
    """should create and add stubs"""
    tmp_stub_path = tmp_path / 'createtest'
    tmp_stub_path.mkdir()
    copytree(str(shared_datadir / 'esp8266_test_stub'),
             str(tmp_stub_path / 'esp8266_test_stub'))
    mock_pyb = mocker.patch("micropy.main.utils.PyboardWrapper")
    mock_pyb.return_value.copy_dir.return_value = Path(str(tmp_stub_path))
    mock_pyb.side_effect = [SystemExit,
                            mock_pyb.return_value, mock_pyb.return_value]
    mp = main.MicroPy()
    stub = mp.create_stubs("/dev/PORT")
    assert stub is None
    mock_pyb.return_value.run.side_effect = [Exception, mocker.ANY]
    stub = mp.create_stubs("/dev/PORT")
    assert stub is None
    stub = mp.create_stubs("/dev/PORT")
    assert isinstance(stub, stubs.DeviceStub)
