from __future__ import annotations

import stat
import sys
from pathlib import PurePosixPath
from typing import Type
from unittest.mock import ANY, MagicMock

import pytest
from micropy.exceptions import PyDeviceError
from micropy.pyd import backend_rshell, backend_upydevice, consumers
from micropy.pyd.abc import MetaPyDeviceBackend, PyDeviceConsumer
from micropy.pyd.pydevice import PyDevice
from pytest_mock import MockFixture
from typing_extensions import Literal


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
    mock_rsh.connect = mocker.Mock()
    mock_rsh.find_serial_device_by_port = mocker.Mock()
    mock_rsh.cp = mocker.Mock()
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

IS_WIN_PY310 = sys.version_info >= (3, 10) and sys.platform.startswith("win")


@pytest.fixture(params=[True, False])
def with_consumer(request: pytest.FixtureRequest, mocker: MockFixture):
    if request.param is True:
        consumer_mock = mocker.MagicMock(PyDeviceConsumer)
        return dict(consumer=consumer_mock)
    return dict()


class TestPyDeviceBackend:
    backend: Literal["upy", "rsh"]
    pyd_cls: Type[MetaPyDeviceBackend]

    @pytest.fixture(
        params=[
            "upy",
            pytest.param(
                "rsh",
                marks=pytest.mark.skipif(
                    IS_WIN_PY310,
                    reason="skipping due to rshell/pyreadline broken for >=py310 on windows.",
                ),
            ),
        ]
    )
    def pymock_setup(self, request: pytest.FixtureRequest):
        self.backend = request.param
        self.pyd_cls = (
            backend_upydevice.UPyDeviceBackend
            if self.backend == "upy"
            else backend_rshell.RShellPyDeviceBackend
        )

    @pytest.fixture
    def pymock(self, pymock_setup, request: pytest.FixtureRequest, mock_upy_uos):
        mod_mock = request.getfixturevalue(f"mock_{self.backend}")
        m = MockAdapter(self.backend, mod_mock, mock_upy_uos)
        yield m
        m.mock.reset_mock()

    def test_init(self, pymock):
        m = pymock
        pyd = self.pyd_cls().establish(MOCK_PORT)
        if self.backend == "upy":
            m.mock.Device.assert_called_once_with(MOCK_PORT, init=True, autodetect=True)
        else:
            assert m.mock.ASCII_XFER is False
            assert m.mock.QUIET is True
        assert pyd.location == MOCK_PORT

    def test_init__connect_fail(self, pymock):
        m = pymock
        m.connect.side_effect = [SystemExit, SystemExit]
        with pytest.raises(PyDeviceError):
            self.pyd_cls().establish(MOCK_PORT).connect()

    def test_connected__default(self, pymock):
        m = pymock
        pyd = self.pyd_cls()
        assert not pyd.connected
        if m.is_upy:
            with pytest.raises(PyDeviceError):
                pyd._ensure_connected()

    def test_connected(self, pymock):
        m = pymock
        pyd = self.pyd_cls().establish(MOCK_PORT)
        pyd.connect()
        assert pyd.connected

    def test_disconnect(self, pymock):
        m = pymock
        pyd = self.pyd_cls().establish(MOCK_PORT)
        pyd.disconnect()
        if m.is_upy:
            m.mock.Device.return_value.disconnect.assert_called_once()

    def test_reset(self, pymock, mocker: MockFixture):
        mocker.patch("time.sleep")
        m = pymock
        pyd = self.pyd_cls().establish(MOCK_PORT)
        pyd.reset()
        if m.is_upy:
            m.device.reset.assert_called_once()
            m.device.connect.assert_called_once()

    def test_eval(self, pymock, mocker: MockFixture, with_consumer):
        m = pymock
        pyd = self.pyd_cls().establish(MOCK_PORT)
        pyd.connect()
        pyd._pydevice.exec_raw = mocker.Mock(return_value=["", ""])
        pyd.eval("abc", **with_consumer)
        has_cons = "consumer" in with_consumer
        if m.is_upy:
            if has_cons:
                m.device.cmd.assert_called_once_with("abc", follow=True, pipe=mocker.ANY)
            else:
                m.device.cmd.assert_called_once_with("abc")
        else:
            if has_cons:
                pyd._pydevice.exec_raw.assert_called_once_with("abc", data_consumer=mocker.ANY)
            else:
                pyd._pydevice.exec_raw.assert_called_once_with("abc", data_consumer=None)

    def test_eval_script(self, pymock, mocker: MockFixture, with_consumer):
        m = pymock
        pyd = self.pyd_cls().establish(MOCK_PORT)
        pyd.connect()
        pyd._pydevice.exec_raw = mocker.Mock(return_value=[b"", b""])
        pyd.eval_script(b"import something", "somefile.py", **with_consumer)
        if m.is_upy:
            if "consumer" in with_consumer:
                with_consumer["consumer"].on_start.assert_called_once()
            m.device.cmd.assert_any_call("import ubinascii")
            mock_random = mocker.patch("random.sample", return_value="abc.py")
            pyd = self.pyd_cls().establish(MOCK_PORT)
            pyd.connect()
            pyd.eval_script(b"import something", None, **with_consumer)
            mock_random.assert_called_once()

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
        pyd = self.pyd_cls().establish(MOCK_PORT)
        m.device.cmd.side_effect = self.read_file_effects
        res = pyd.read_file("/some/path")
        assert res == "Hi there"

    def test_pull_file(self, pymock, tmp_path):
        m = pymock
        pyd = self.pyd_cls().establish(MOCK_PORT)
        pyd.connect()
        if m.is_upy:
            m.device.cmd.side_effect = self.read_file_effects
            pyd.pull_file("/some/path", (tmp_path / "out.txt"))
            assert (tmp_path / "out.txt").read_text() == "Hi there"
        else:
            m.mock.find_serial_device_by_port.return_value.name_path = "/"
            pyd.pull_file("/some/path", (tmp_path / "out.txt"))
            m.mock.cp.assert_called_once_with("/some/path", str(tmp_path / "out.txt"))

    def test_iter_files(self, pymock):
        m = pymock
        if m.is_rsh:
            return
        pyd = self.pyd_cls().establish(MOCK_PORT)
        pyd.connect()
        m.device.cmd.side_effect = [
            None,
            None,
            None,
            [("name", "stat", "", "")],
            None,
            [("name", stat.S_IFDIR, "", "")],
            None,
            [("underName", "", "", "")],
        ]
        assert list(pyd.iter_files("/some/path")) == []
        m.device.cmd.assert_any_call("import uos", silent=True)
        m.device.cmd.assert_any_call("list(uos.ilistdir('/some/path'))", silent=True, rtn_resp=True)
        assert list(pyd.iter_files("/some/path")) == [PurePosixPath("/some/path/name")]
        assert list(pyd.iter_files("/some/path")) == [PurePosixPath("/some/path/name/underName")]


class TestPyDevice:
    @pytest.fixture
    def mock_backend(self, mocker: MockFixture):
        mock = mocker.MagicMock(MetaPyDeviceBackend)
        mock.return_value.establish.return_value = mock.return_value
        return mock

    @pytest.fixture(
        params=[
            ["dir", "/some/dir"],
            ["file", "/some/file.txt"],
            ["dir", r"c:\\some\\dos\\dir"],
            ["file", r"c:\\some\\dos\\file.txt"],
        ]
    )
    def path_type(self, request: pytest.FixtureRequest):
        return request.param

    @pytest.mark.parametrize(
        "pyd_kwargs",
        [
            dict(),
            dict(auto_connect=False),
            dict(delegate_cls=lambda *x: x, stream_consumer="stream", message_consumer="message"),
        ],
    )
    def test_init(self, mock_backend, pyd_kwargs):
        pyd = PyDevice(MOCK_PORT, backend=mock_backend, **pyd_kwargs)
        mock_backend.assert_called_once()
        mock_backend.return_value.establish.assert_called_once_with(MOCK_PORT)
        if pyd_kwargs.get("auto_connect", True):
            mock_backend.return_value.connect.assert_called_once()
        if "delegate_cls" in pyd_kwargs:
            assert pyd.consumer == (
                "stream",
                "message",
            )

    def test_connect(self, mock_backend):
        pyd = PyDevice(MOCK_PORT, backend=mock_backend, auto_connect=False)
        pyd.connect()
        mock_backend.return_value.connect.assert_called_once()

    def test_disconnect(self, mock_backend):
        pyd = PyDevice(MOCK_PORT, backend=mock_backend)
        pyd.disconnect()
        mock_backend.return_value.disconnect.assert_called_once()

    def test_copy_from(self, mock_backend, path_type, mocker):
        pyd = PyDevice(MOCK_PORT, backend=mock_backend)
        ptype, p = path_type
        pyd.copy_from(p, "/host/path")
        if ptype == "dir":
            mock_backend.return_value.copy_dir.assert_called_once_with(
                p, "/host/path", consumer=mocker.ANY
            )
        else:
            mock_backend.return_value.pull_file.assert_called_once_with(
                p, "/host/path", consumer=mocker.ANY
            )

    def test_copy_to(self, mock_backend, path_type, mocker):
        pyd = PyDevice(MOCK_PORT, backend=mock_backend)
        ptype, p = path_type
        if ptype == "dir":
            with pytest.raises(RuntimeError):
                pyd.copy_to("/host/path", p)
        else:
            pyd.copy_to("/host/path/f.txt", p)
            mock_backend.return_value.push_file.assert_called_once_with(
                "/host/path/f.txt", p, consumer=mocker.ANY
            )


class TestConsumers:
    @pytest.mark.parametrize(
        "on_desc,expected_tqdm",
        [
            [None, dict(total=5, unit="B", unit_scale=True, unit_divisor=1024, bar_format=ANY)],
            [
                lambda n, cfg: ("other", dict(override=True)),
                dict(
                    total=5,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    bar_format=ANY,
                    override=True,
                ),
            ],
        ],
    )
    def test_progress_consumer(self, mocker: MockFixture, on_desc, expected_tqdm):
        tqdm_mock = mocker.patch.object(consumers, "tqdm")
        cons = consumers.ProgressStreamConsumer(on_desc)
        cons.on_start(name="abc", size=5)
        tqdm_mock.assert_called_once_with(**expected_tqdm)
        cons.on_update(size=1)
        tqdm_mock.return_value.update.assert_called_once_with(1)
        cons.on_end()
        tqdm_mock.return_value.close.assert_called_once()

    def test_delegate(self):
        delegate = consumers.ConsumerDelegate()
        assert delegate.on_message("") is None
        delegate = consumers.ConsumerDelegate(consumers.MessageHandlers(on_message=lambda m: m))
        assert delegate.on_message("a") == "a"

    @pytest.mark.skipif(
        IS_WIN_PY310, reason="skipping due to rshell/pyreadline broken for >=py310 on windows."
    )
    def test_rsh_consumer(self):
        calls = []
        message_cons = consumers.MessageHandlers(on_message=lambda m: calls.append(m))
        rsh_cons = backend_rshell.RShellConsumer(message_cons.on_message)
        chars = iter(list("a line.\nnext line.\n"))
        for i in chars:
            rsh_cons.on_message(i.encode())
        assert len(calls) == 2
        assert calls == ["a line.", "next line."]
