from __future__ import annotations

import binascii
import io
import random
import stat
import string
import time
from functools import wraps
from pathlib import Path, PurePosixPath
from typing import AnyStr, Callable, Generator, TypeVar, Union

import upydevice
from boltons import iterutils
from micropy.exceptions import PyDeviceConnectionError, PyDeviceError
from typing_extensions import ParamSpec, TypeAlias
from upydevice.phantom import UOS as UPY_UOS

from .abc import DevicePath, HostPath, MessageConsumer, MetaPyDeviceBackend, PyDeviceConsumer

AnyUPyDevice: TypeAlias = Union[upydevice.SerialDevice, upydevice.WebSocketDevice]

BUFFER_SIZE = 512

T = TypeVar("T")
P = ParamSpec("P")


class UOS(UPY_UOS):
    @upydevice.upy_cmd_c_r()
    def stat(self, path):
        return self.dev_dict


def retry(fn: Callable[P, T]) -> Callable[P, T | None]:
    @wraps(fn)
    def _wrapper(self_: UPyDeviceBackend, *args: P.args, **kwargs: P.kwargs) -> T | None:
        _result: T | None = None
        retry_count = 0

        while retry_count < 4:
            try:
                _result = fn(self_, *args, **kwargs)  # type: ignore
            except Exception as e:
                retry_count += 1
                self_.BUFFER_SIZE = BUFFER_SIZE // pow(2, retry_count + 1)
                print("reducing buffer size to:", self_.BUFFER_SIZE)
                print(e)
                self_.reset()
            else:
                break
        return _result

    return _wrapper  # type: ignore


class UPyDeviceBackend(MetaPyDeviceBackend):
    BUFFER_SIZE: int = BUFFER_SIZE

    _pydevice: AnyUPyDevice
    _uos: UOS | None = None

    def _ensure_connected(self):
        if not self.connected:
            raise PyDeviceError(f"No currently connected device found!")

    def _rand_device_path(self) -> DevicePath:
        name = "".join(random.sample(string.ascii_lowercase, 6))
        return self.resolve_path(DevicePath(name))

    @property
    def uos(self) -> UOS:
        self._ensure_connected()
        if not self._uos:
            self._uos = UOS(self._pydevice)
        return self._uos

    def _pyb_root(self) -> DevicePath:
        results = self.uos.stat("/flash")
        if "Traceback" or "ENOENT" in results:
            return DevicePath("/")
        return DevicePath("/flash")

    def resolve_path(self, path: DevicePath | str | Path) -> DevicePath:
        _root = PurePosixPath(self._pyb_root())
        _path = PurePosixPath(path)
        if _path.is_absolute():
            if _root == _path or _root in list(_path.parents):
                return DevicePath(str(_path))
            _path = _path.relative_to(list(_path.parents)[-1])
        return DevicePath(str(_root / _path))

    def establish(self, target: str) -> UPyDeviceBackend:
        self.location = target
        self._pydevice = upydevice.Device(target, init=True, autodetect=True)
        return self

    def connect(self):
        try:
            self._pydevice.connect()
        except (SystemExit, Exception) as e:
            raise PyDeviceConnectionError(self.location) from e

    def disconnect(self):
        if self.connected:
            self._pydevice.disconnect()

    def reset(self):
        self._pydevice.reset()
        time.sleep(2)
        self._pydevice.connect()
        time.sleep(4)

    @property
    def connected(self) -> bool:
        return False if getattr(self, "_pydevice", None) is None else self._pydevice.connected

    def list_dir(self, path: DevicePath) -> list[DevicePath]:
        return [DevicePath(p) for p in self.uos.listdir(self.resolve_path(path))]

    def iter_files(self, path: DevicePath) -> Generator[DevicePath, None, None]:
        path = self.resolve_path(path)
        self._pydevice.cmd("import uos", silent=True)
        results = self._pydevice.cmd(f"list(uos.ilistdir('{path}'))", silent=True, rtn_resp=True)
        if not results:
            return
        for name, type_, _, _ in results:
            abs_path = PurePosixPath(path) / name
            if type_ == stat.S_IFDIR:
                yield from self.iter_files(abs_path)
            else:
                yield abs_path

    def copy_dir(self, source_path: DevicePath, target_path: HostPath, **kwargs):
        target_path = Path(str(target_path))  # type: ignore
        source_path = self.resolve_path(source_path)
        for file_path in self.iter_files(source_path):
            rel_path = PurePosixPath(file_path).relative_to(
                list(PurePosixPath(file_path).parents)[-1]
            )
            # handles os-path conversion
            file_dest = Path(target_path / rel_path)
            file_dest.parent.mkdir(parents=True, exist_ok=True)
            self.pull_file(file_path, HostPath(str(file_dest)), **kwargs)

    def push_file(self, source_path: HostPath, target_path: DevicePath, **kwargs) -> None:
        src_path = Path(str(source_path))
        src_contents = src_path.read_text()
        self.write_file(src_contents, target_path, **kwargs)

    def pull_file(self, source_path: DevicePath, target_path: HostPath, **kwargs) -> None:
        src_path = self.resolve_path(source_path)
        targ_path = Path(str(target_path))
        source_contents = self.read_file(src_path, **kwargs)
        if source_contents is None:
            # TODO: properly report failure to read/copy file.
            return None
        targ_path.write_text(source_contents)

    def _iter_hex_chunks(self, content: str):
        chunked_content = iterutils.chunked_iter(content, self.BUFFER_SIZE)
        for chunk in chunked_content:
            hex_chunk = binascii.hexlify(chunk.encode())
            yield hex_chunk

    @retry
    def write_file(
        self, contents: str, target_path: DevicePath, *, consumer: PyDeviceConsumer | None = None
    ) -> None:
        target_path = self.resolve_path(target_path)
        self._pydevice.cmd("import ubinascii")
        self._pydevice.cmd(f"f = open('{str(target_path)}', 'wb')")
        content_size = len(binascii.hexlify(contents.encode())) // 2
        if consumer:
            consumer.on_start(name=f"Writing {str(target_path)}", size=content_size)
        for chunk in self._iter_hex_chunks(contents):
            cmd = f"contents = ubinascii.unhexlify('{chunk.decode()}'); f.write(contents)"
            self._pydevice.cmd(cmd, silent=True)
            if consumer:
                consumer.on_update(size=len(chunk) // 2)
        if consumer:
            consumer.on_end()
        self._pydevice.cmd("f.close()")

    @retry
    def read_file(
        self, target_path: DevicePath, *, consumer: PyDeviceConsumer | None = None
    ) -> str:
        target_path = self.resolve_path(target_path)
        self._pydevice.cmd("import ubinascii", silent=True)
        self._pydevice.cmd(f"f = open('{str(target_path)}', 'rb')", silent=True)
        content_size = self._pydevice.cmd(f"f.seek(0,2)", rtn_resp=True, silent=True)
        self._pydevice.cmd("f.seek(0)", silent=True)
        buffer = io.BytesIO()
        if consumer:
            consumer.on_start(name=f"Reading {target_path}", size=content_size // 2)
        last_pos = 0
        while True:
            pos = self._pydevice.cmd(f"f.tell()", rtn_resp=True, silent=True)
            if consumer:
                consumer.on_update(size=(pos - last_pos) // 2)
            last_pos = pos
            if pos == content_size:
                if consumer:
                    consumer.on_end()
                break
            next_chunk = self._pydevice.cmd(
                f"f.read({self.BUFFER_SIZE})", rtn_resp=True, silent=True
            )
            buffer.write(next_chunk)
        self._pydevice.cmd("f.close()")
        value = buffer.getvalue().decode()
        return value

    def eval(self, command: str, *, consumer: MessageConsumer = None):
        if consumer:
            return self._pydevice.cmd(
                command, follow=True, pipe=lambda m, *args, **kws: consumer.on_message(m)
            )
        return self._pydevice.cmd(command)

    def eval_script(
        self,
        contents: AnyStr,
        target_path: DevicePath | None = None,
        *,
        consumer: PyDeviceConsumer = None,
    ):
        _target_path = (
            self.resolve_path(target_path) if target_path else f"{self._rand_device_path()}.py"
        )
        if isinstance(contents, bytes):
            contents = contents.decode()  # type: ignore
        self.write_file(str(contents), DevicePath(_target_path), consumer=consumer)
        self.eval(f"import {Path(_target_path).stem}", consumer=consumer)
        self.uos.remove(str(_target_path))
