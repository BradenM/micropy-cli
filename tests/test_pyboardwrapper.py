# -*- coding: utf-8 -*-

import pytest
from micropy.utils import PyboardWrapper


@pytest.fixture
def connect_mock(mocker):
    mocked_connect = mocker.patch("rshell.main.connect")
    return mocked_connect


@pytest.fixture
def root_mock(monkeypatch):
    monkeypatch.setattr(PyboardWrapper, "pyb_root", "/mock/")
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
