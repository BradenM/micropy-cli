from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, AnyStr, Callable, cast

from micropy.exceptions import PyDeviceConnectionError

from . import abc
from .abc import DevicePath, HostPath

if TYPE_CHECKING:
    from typing import type_check_only

    @type_check_only
    class RShell:
        ASCII_XFER: bool
        QUIET: bool

        def connect(self, port: str):
            ...


CREATE_STUBS_INSTALLED = False

try:
    import rshell.main as rsh
    from rshell.pyboard import Pyboard, PyboardError
except ImportError:
    rsh: RShell = cast(RShell, object())
    PyboardError = RuntimeError
    Pyboard = object()
    CREATE_STUBS_INSTALLED = False
else:
    CREATE_STUBS_INSTALLED = True


class RShellConsumer:
    def __init__(self, on_message: Callable[[str], Any]):
        self._outline = []
        self.format_output = None
        self.on_message = on_message

    def _output(self, data):
        """Yields everything up to a newline.

        Args:
            data (str): Anything to yield before newline

        """
        if data == "\n":
            line = "".join(self._outline)
            self._outline = []
            yield line
        self._outline.append(data)

    def consumer(self, char: bytes):
        """Pyboard data consumer.

        When a full line of output is detected,
        it is formatted then logged to stdout
        and log file.

        Args:
            char (byte): Byte from PyBoard

        Returns:
            str: Converted char

        """
        char = char.decode("utf-8")
        line = next(self._output(char), None)
        if line:
            if self.format_output:
                line = self.format_output(line)
            self.on_message(line)
        return char


class RShellPyDevice(abc.PyDevice[Pyboard]):
    _connected: bool = False
    _verbose: bool = False
    _rsh: rsh

    def __init__(
        self, location: str, verbose: bool = False, data_consumer=None, auto_connect: bool = True
    ):
        super().__init__(location, auto_connect)
        self._verbose = verbose
        self._data_consumer = data_consumer

    @property
    def _pyb_root(self) -> str:
        """pyboard root dirname."""
        if self.connected:
            dev = rsh.find_serial_device_by_port(self.location)
            return getattr(dev, "name_path", "/pyboard/")

    @property
    def connected(self) -> bool:
        return self._connected

    def _pyb_path(self, path: str) -> DevicePath:
        _path = path
        if path[0] == "/":
            _path = path[1:]
        pyb_path = f"{self._pyb_root}{_path}"
        return DevicePath(pyb_path)

    def establish(self, *_) -> rsh:
        self._rsh = rsh
        self._rsh.ASCII_XFER = False
        self._rsh.QUIET = not self._verbose
        return self._rsh

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

    def copy_file(self, source_path: HostPath, target_path: DevicePath = None) -> None:
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
        dest = self._pyb_path(_dest)
        self._rsh.cp(str(src_path), str(dest))
        return dest

    def list_dir(self, path: DevicePath) -> list[DevicePath]:
        """List directory on pyboard.

        Args:
            path: path to directory

        """
        dir_path = self._pyb_path(path)
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
        dir_path = self._pyb_path(source_path)
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
        self._pydevice.enter_raw_repl()
        try:
            yield self._pydevice
        finally:
            self._pydevice.exit_raw_repl()

    def _exec(self, command):
        """Execute bytes on pyboard."""
        consumer = None if self._data_consumer is None else self._data_consumer.consumer
        ret, ret_err = self._pydevice.exec_raw(command, data_consumer=consumer)
        if ret_err:
            raise PyboardError("exception", ret, ret_err)
        return ret

    def run_script(self, file: Path | AnyStr, *_):
        """Execute a local script on the pyboard.

        Args:
            file (str): path to file or string to run

        """
        try:
            with file.open("rb") as f:
                pyfile = f.read()
        except AttributeError:
            pyfile = file.encode("utf-8")
        with self.repl():
            try:
                out_bytes = self._exec(pyfile)
            except PyboardError as e:
                raise Exception(str(e))
            out = out_bytes.decode("utf-8")
            return out
