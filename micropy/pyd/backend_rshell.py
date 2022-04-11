from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, AnyStr, cast

from micropy.exceptions import PyDeviceConnectionError
from micropy.pyd.abc import (
    DevicePath,
    HostPath,
    MessageConsumer,
    MessageHandler,
    MetaPyDeviceBackend,
    PyDeviceConsumer,
)

if TYPE_CHECKING:
    from typing import type_check_only  # pragma: no cover

    @type_check_only  # pragma: no cover
    class RShell:
        ASCII_XFER: bool
        QUIET: bool

        def connect(self, port: str):
            ...


try:
    import rshell.main as rsh  # type: ignore
    from rshell.pyboard import Pyboard, PyboardError  # type: ignore
except (
    ImportError,
    ModuleNotFoundError,
):  # pragma: no cover
    rsh = object()  # type: ignore
    if TYPE_CHECKING:
        rsh: RShell = cast(RShell, object())  # type: ignore
    PyboardError = RuntimeError
    Pyboard = object()


class RShellConsumer:
    consumer: MessageHandler

    def __init__(self, child_consumer: MessageHandler):
        self._outline: list[str] = []
        self.consumer = child_consumer

    def _output(self, data: str):
        """Yields everything up to a newline.

        Args:
            data (str): Anything to yield before newline

        """
        if data == "\n":
            line = "".join(self._outline)
            self._outline = []
            yield line
        self._outline.append(data)

    def on_message(self, char: bytes):
        """Pyboard data consumer.

        When a full line of output is detected,
        it is formatted then logged to stdout
        and log file.

        Args:
            char (byte): Byte from PyBoard

        Returns:
            str: Converted char

        """
        _char = char.decode("utf-8")
        line = next(self._output(_char), None)
        if line:
            self.consumer(line)
        return char


class RShellPyDeviceBackend(MetaPyDeviceBackend):
    _connected: bool = False
    _verbose: bool = False
    _rsh: rsh
    _pydevice: Pyboard

    _dev_port: str
    _repl_active: bool = False

    @property
    def _pyb_root(self) -> str:
        """pyboard root dirname."""
        if self.connected:
            dev = rsh.find_serial_device_by_port(self.location)
            return getattr(dev, "name_path", "/pyboard/")
        return ""

    @property
    def connected(self) -> bool:
        return self._connected

    def resolve_path(self, path: str | DevicePath | Path) -> DevicePath:
        _path = path
        if str(path)[0] == "/":
            _path = str(path)[1:]
        pyb_path = f"{self._pyb_root}{_path}"
        return DevicePath(pyb_path)

    def establish(self, target: str) -> RShellPyDeviceBackend:
        self._rsh = rsh
        self._rsh.ASCII_XFER = False
        self._rsh.QUIET = not self._verbose
        self.location = target
        return self

    def connect(self) -> None:
        try:
            self._rsh.connect(self.location)
        except (SystemExit, Exception) as e:
            raise PyDeviceConnectionError(self.location) from e
        self._connected = True
        dev = self._rsh.find_serial_device_by_port(self.location)
        if dev is None:
            raise PyDeviceConnectionError(self.location)
        self._pydevice = dev.pyb

    def disconnect(self) -> None:
        return

    def reset(self) -> None:
        return

    def push_file(self, source_path: HostPath, target_path: DevicePath = None, **_) -> None:
        """Copies file to pyboard.

        Args:
            source_path (str): path to file
            target_path (str, optional): dest on pyboard. Defaults to None.
                If None, file is copied to pyboard root.

        Returns:
            str: path to dest on pyboard

        """
        src_path = Path(source_path).resolve()
        _dest = target_path or src_path.name
        dest = self.resolve_path(_dest)
        self._rsh.cp(str(src_path), str(dest))

    def pull_file(self, source_path: DevicePath, target_path: HostPath, **kwargs) -> None:
        host_dest = Path(target_path).resolve()
        device_src = self.resolve_path(source_path)
        self._rsh.cp(str(device_src), str(host_dest))

    def list_dir(self, path: DevicePath) -> list[DevicePath]:
        """List directory on pyboard.

        Args:
            path: path to directory

        """
        dir_path = self.resolve_path(path)
        tree = self._rsh.auto(rsh.listdir, str(dir_path))
        return tree

    def copy_dir(
        self, source_path: HostPath | DevicePath, target_path: HostPath | DevicePath, **rsync
    ):
        """Copy directory from pyboard to machine.

        Args:
            source_path: path to directory
            target_path: destination to copy to
            rsync (dict, optional): additonal args to pass to rsync call.
                Defaults to {}

        """
        dir_path = self.resolve_path(source_path)
        dest_path = Path(str(target_path))
        rsync_args = {
            "recursed": True,
            "mirror": False,
            "dry_run": False,
            "print_func": lambda *args: None,
            "sync_hidden": False,
        }
        self._rsh.rsync(dir_path, str(dest_path), **(rsync_args | rsync))
        return dest_path

    @contextmanager
    def repl(self):
        """Pyboard raw repl context manager."""
        if self._repl_active:
            yield self._pydevice
        else:
            self._pydevice.enter_raw_repl()
            self._repl_active = True
            try:
                yield self._pydevice
            finally:
                self._pydevice.exit_raw_repl()
                self._repl_active = False

    def eval(self, command: str, *, consumer: MessageConsumer = None):
        """Execute bytes on pyboard."""
        _handler = None if consumer is None else RShellConsumer(consumer.on_message).on_message
        ret, ret_err = self._pydevice.exec_raw(command, data_consumer=_handler)
        if ret_err:
            raise PyboardError("exception", ret, ret_err)
        return ret

    def eval_script(
        self,
        contents: AnyStr,
        target_path: DevicePath | None = None,
        *,
        consumer: PyDeviceConsumer = None,
    ):
        _contents: str | bytes = contents
        if isinstance(_contents, bytes):
            _contents = _contents.decode()
        with self.repl():
            try:
                out_bytes = self.eval(_contents, consumer=consumer)
            except PyboardError as e:
                raise Exception(str(e))
            out = out_bytes.decode("utf-8")
            return out
