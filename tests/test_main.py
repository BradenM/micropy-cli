# -*- coding: utf-8 -*-

import json
from pathlib import Path
from shutil import copytree, rmtree

import pytest

import micropy.exceptions as exc
from micropy import data, main
from micropy.stubs import stubs


def test_setup(mock_micropy_path):
    """Tests MicroPy Initial Setup"""
    expect_mp_dir = mock_micropy_path
    expect_stubs_dir = mock_micropy_path / 'stubs'
    mp = main.MicroPy()
    assert expect_mp_dir.exists()
    assert expect_stubs_dir.exists()
    # Test after inital setup
    mp_ = main.MicroPy()
    assert len(mp_.stubs) == len(mp.stubs)


def test_add_stub(mock_micropy, shared_datadir):
    """Test Adding Valid Stub"""
    fware_path = shared_datadir / 'fware_test_stub'
    stub_path = shared_datadir / 'esp8266_test_stub'
    stubs = mock_micropy.stubs
    fware_stub = stubs.add(fware_path, data.STUB_DIR)
    stub = stubs.add(stub_path, data.STUB_DIR)
    assert stub in list(mock_micropy.stubs)
    assert stub.path in data.STUB_DIR.iterdir()
    assert stub.path.exists()
    assert fware_stub in list(mock_micropy.stubs._firmware)


def test_create_stub(mock_micropy, mocker, shared_datadir, tmp_path):
    """should create and add stubs"""
    mock_micropy.stubs.add((shared_datadir / 'fware_test_stub'))
    tmp_stub_path = tmp_path / 'createtest'
    tmp_stub_path.mkdir()
    copytree(str(shared_datadir / 'stubber_test_stub'),
             str(tmp_stub_path / 'stubber_test_stub'))
    mock_pyb = mocker.patch("micropy.main.utils.PyboardWrapper")
    mock_pyb.return_value.copy_dir.return_value = Path(str(tmp_stub_path))
    mock_pyb.side_effect = [SystemExit,
                            mock_pyb.return_value, mock_pyb.return_value,
                            mock_pyb.return_value]
    mp = main.MicroPy()
    mocker.spy(mp.stubs, 'add')
    stub = mp.create_stubs("/dev/PORT")
    assert stub is None
    mock_pyb.return_value.run.side_effect = [Exception, mocker.ANY, mocker.ANY]
    stub = mp.create_stubs("/dev/PORT")
    assert stub is None
    stub = mp.create_stubs("/dev/PORT")
    mp.stubs.add.assert_any_call((tmp_stub_path / 'esp32-1.11.0'))
    rmtree((tmp_stub_path / 'esp32-1.11.0'))
    assert isinstance(stub, stubs.DeviceStub)
    # Test outpath with firmware
    mod_path = tmp_stub_path / 'stubber_test_stub' / 'modules.json'
    mod_data = json.load(mod_path.open())
    mod_data['firmware']['name'] = 'micropython'
    json.dump(mod_data, mod_path.open('w+'))
    stub = mp.create_stubs("/dev/PORT")
    mp.stubs.add.assert_any_call((tmp_stub_path / 'esp32-micropython-1.11.0'))


def test_create_stubs_pymin_check(mocker, mock_micropy):
    """should exit without pymin"""
    mocker.patch("micropy.main.utils.PyboardWrapper")
    mocker.patch("micropy.main.StubManager")
    mock_stubber = mocker.patch.object(main, "stubber")
    mock_exit = mocker.spy(main.sys, 'exit')
    mock_stubber.minify_script.side_effect = [AttributeError, mocker.ANY]
    # Should exit
    with pytest.raises(SystemExit):
        mock_micropy.create_stubs("/dev/PORT")
    # Should continue
    mock_micropy.create_stubs("/dev/PORT")
    mock_exit.assert_called_once_with(1)


def test_stub_error():
    with pytest.raises(exc.StubError):
        raise exc.StubError(None)


def test_resolve_project(mocker, mock_micropy):
    mock_proj = mocker.patch.object(main, "Project").return_value
    mock_proj.exists.return_value = False
    assert mock_micropy.resolve_project('.') is None
    mock_proj.exists.return_value = True
    assert mock_micropy.resolve_project('.')
