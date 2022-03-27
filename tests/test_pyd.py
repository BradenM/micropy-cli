from __future__ import annotations

from typing import Literal, Type
from unittest.mock import MagicMock

import pytest
from micropy.exceptions import PyDeviceError
from micropy.pyb import backend_rshell, backend_upydevice
from micropy.pyb.abc import PyDevice
from pytest_mock import MockFixture


@pytest.fixture
def mock_upy(mocker: MockFixture):
    mock_upy = mocker.patch.object(backend_upydevice, "upydevice", autospec=True)
    return mock_upy


@pytest.fixture
def mock_upy_uos(mocker: MockFixture):
    mock_uos = mocker.patch.object(backend_upydevice, "UOS", autospec=True)
    return mock_uos


@pytest.fixture
def mock_rsh(mocker: MockFixture):
    mock_rsh = mocker.patch.object(backend_rshell, "rsh", autospec=True)
    return mock_rsh


class MockAdapter:
    backend: Literal["upy", "rsh"]
    mock: MagicMock
    mock_uos: MagicMock

    def __init__(self, backend: Literal["upy", "rsh"], mock: MagicMock, mock_uos=None):
        self.backend = backend
        self.mock = mock
        if mock_uos:
            self.mock_uos = mock_uos

    @property
    def is_rsh(self) -> bool:
        return self.backend == "rsh"

    @property
    def is_upy(self) -> bool:
        return self.backend == "upy"

    @property
    def connect(self) -> MagicMock:
        return self.mock.Device.return_value.connect if self.is_upy else self.mock.connect

    @property
    def device(self):
        return self.mock.Device.return_value if self.is_upy else self.mock


MOCK_PORT = "/dev/port"


@pytest.fixture(params=["upy", "rsh"], scope="class")
def pymock_setup(request: pytest.FixtureRequest) -> MockAdapter:
    request.cls.backend = request.param
    request.cls.pyd_cls = (
        backend_upydevice.UPYPyDevice
        if request.cls.backend == "upy"
        else backend_rshell.RShellPyDevice
    )
    _cls = (
        backend_upydevice.UPYPyDevice if request.param == "upy" else backend_rshell.RShellPyDevice
    )
    _consumer = (
        backend_upydevice.UPYConsumer if request.param == "upy" else backend_rshell.RShellConsumer
    )
    yield


@pytest.fixture
def pymock(request: MockFixture, mock_upy_uos):
    mod_mock = request.getfixturevalue(f"mock_{request.cls.backend}")
    return MockAdapter(request.cls.backend, mod_mock, mock_upy_uos)


@pytest.mark.usefixtures("pymock_setup")
class TestPyDevice:
    backend: Literal["upy", "rsh"]
    pyd_cls: Type[PyDevice]

    def test_init(self, pymock):
        m = pymock
        pyd = self.pyd_cls(MOCK_PORT)
        if self.backend == "upy":
            m.mock.Device.assert_called_once_with(MOCK_PORT, init=True, autodetect=True)
        else:
            assert m.mock.ASCII_XFER is False
            assert m.mock.QUIET is True
        m.connect.assert_called_once()
        assert pyd.connected
        assert pyd.location == MOCK_PORT

    def test_init__connect_fail(self, pymock):
        m = pymock
        m.connect.side_effect = [SystemExit, SystemExit]
        with pytest.raises(PyDeviceError):
            self.pyd_cls(MOCK_PORT)

    def test_disconnect(self, pymock):
        m = pymock
        pyd = self.pyd_cls(MOCK_PORT)
        pyd.disconnect()
        if m.is_upy:
            m.mock.Device.return_value.disconnect.assert_called_once()

    def test_reset(self, pymock, mocker: MockFixture):
        mocker.patch("time.sleep")
        m = pymock
        pyd = self.pyd_cls(MOCK_PORT)
        pyd.reset()
        if m.is_upy:
            m.device.reset.assert_called_once()
            assert m.device.connect.call_count == 2

    @property
    def read_file_effects(self):
        cmd_effects = [
            None,  # import ubin
            None,  # open file
            8,  # content size
            0,  # seek start
            0,  # pos
            b"Hi there",  # read,
            8,  # pos
            None,  # close
        ]
        return cmd_effects

    def test_read_file(self, pymock):
        m = pymock
        if m.is_rsh:
            return
        pyb = self.pyd_cls(MOCK_PORT)
        m.device.cmd.side_effect = self.read_file_effects
        res = pyb.read_file("/some/path")
        assert res == "Hi there"

    def test_copy_file(self, pymock, tmp_path):
        m = pymock
        if m.is_rsh:
            return
        pyb = self.pyd_cls(MOCK_PORT)
        m.device.cmd.side_effect = self.read_file_effects
        pyb.copy_file("/some/path", (tmp_path / "out.txt"))
        assert (tmp_path / "out.txt").read_text() == "Hi there"
