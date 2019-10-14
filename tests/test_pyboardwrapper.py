# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from micropy.utils import PyboardWrapper, pybwrapper

from micropy.utils.pybwrapper import PyboardError


@pytest.fixture
def connect_mock(mocker):
    mocked_connect = mocker.patch("rshell.main.connect")
    return mocked_connect


@pytest.fixture
def root_mock(mocker):
    mocker.patch.object(PyboardWrapper, "pyb_root", "/mock/")
    return "/mock/"


def test_pyboard_connect(connect_mock):
    """should connect"""
    pyb = PyboardWrapper("/dev/PORT")
    connect_mock.assert_called_once_with("/dev/PORT")
    assert pyb.connected


def test_pyboard_fail_connect():
    """should fail"""
    with pytest.raises(SystemExit):
        PyboardWrapper("/dev/BADPORTPARAM")


def test_pyboard_list_dir(mocker, connect_mock, root_mock):
    """should list directory"""
    mocked_auto = mocker.patch("rshell.main.auto")
    mocked_auto.return_value = ['main.py', 'boot.py']
    pyb = PyboardWrapper("/dev/PORT")
    value = pyb.list_dir("/path")
    mocked_auto.assert_called_once_with(mocker.ANY, "/mock/path")
    assert value == ['main.py', 'boot.py']


def test_pyboard_copy_dir(mocker, connect_mock, root_mock, tmp_path):
    """should copy directory"""
    mocked_rsync = mocker.patch("rshell.main.rsync")
    dest_path = tmp_path / 'dest'
    dest_path.mkdir()
    pyb = PyboardWrapper("/dev/PORT")
    out_dir = pyb.copy_dir('/foobar/bar', dest_path)
    assert out_dir == dest_path
    expected_rsync = {
        "recursed": True,
        "mirror": False,
        "dry_run": False,
        "print_func": mocker.ANY,
        "sync_hidden": False
    }
    expected_dir_path = "/mock/foobar/bar"
    mocked_rsync.assert_called_once_with(
        expected_dir_path, str(dest_path), **expected_rsync)


def test_pyboard_copy_file(mocker, connect_mock, root_mock, tmp_path):
    """should copy file"""
    mocked_cp = mocker.patch("rshell.main.cp")
    pyb = PyboardWrapper("/dev/PORT")
    # No Dest Test
    out_file = pyb.copy_file("/foobar/file.py")
    assert Path(out_file) == Path("/mock/file.py")
    mocked_cp.assert_called_once_with(
        str(Path("/foobar/file.py").absolute()), "/mock/file.py")
    # With Dest
    out_file = pyb.copy_file("file.py", "/foobar/file.py")
    assert Path(out_file) == Path("/mock/foobar/file.py")


def test_pyboard_run(mocker, connect_mock, tmp_path):
    """should execute script"""
    tmp_script = tmp_path / 'script.py'
    tmp_script.touch()
    tmp_string = tmp_script.open('r').read()
    pyb_mock = mocker.patch.object(PyboardWrapper, 'pyboard')
    pyb_mock.exec_raw.side_effect = [
        (b"abc", None), (b"abc", None), (b"", PyboardError)]
    pyb = PyboardWrapper("/dev/PORT")
    result = pyb.run(tmp_script)
    assert result == "abc"
    # Should work as string
    result = pyb.run(tmp_string)
    assert result == "abc"
    with pytest.raises(Exception):
        pyb.run(tmp_script)


def test_pyboard_attr(mocker, connect_mock):
    """should return pyboard"""
    find_mock = mocker.patch("rshell.main.find_serial_device_by_port")
    pyb = PyboardWrapper("/dev/PORT")
    pyb.pyboard
    find_mock.assert_called_once_with("/dev/PORT")
    pyb = PyboardWrapper("/dev/PORT2", connect=False)
    pyb.pyboard
    find_mock.assert_called_once()


def test_pyboard_root(mocker, connect_mock):
    """should get root"""
    find_mock = mocker.patch("rshell.main.find_serial_device_by_port")
    pyb = PyboardWrapper("/dev/PORT")
    pyb.pyb_root
    find_mock.assert_called_once_with("/dev/PORT")
    pyb = PyboardWrapper("/dev/PORT2", connect=False)
    pyb.pyb_root
    find_mock.assert_called_once()


def test_pyboard_output(mocker):
    """should consume till a newline"""
    line_bytes = list("a line to consume\n")
    mocker.patch.object(pybwrapper, 'Log')
    pyb = pybwrapper.PyboardWrapper('/dev/foo', connect=False)
    for char in line_bytes:
        pyb._consumer(char.encode('utf-8'))
    pyb.log.info.assert_called_once_with("a line to consume")
    # Test format output
    pyb.format_output = lambda val: val.replace('line', 'string')
    for char in line_bytes:
        pyb._consumer(char.encode('utf-8'))
    pyb.log.info.assert_called_with("a string to consume")
