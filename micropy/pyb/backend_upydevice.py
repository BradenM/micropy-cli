from __future__ import annotations

import binascii
import io
import random
import stat
import string
import time
from functools import wraps
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Generator, TypeVar, Union

import upydevice
from boltons import iterutils
from micropy.exceptions import PyDeviceConnectionError, PyDeviceError
from tqdm import tqdm
from typing_extensions import ParamSpec, TypeAlias
from upydevice.phantom import UOS as UPY_UOS

from . import abc
from .abc import DevicePath, HostPath

AnyUPyDevice: TypeAlias = Union[upydevice.SerialDevice, upydevice.WebSocketDevice]

BUFFER_SIZE = 512

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
P = ParamSpec("P")


class UOS(UPY_UOS):
    @upydevice.upy_cmd_c_r()
    def stat(self, path):
        return self.dev_dict


class UPYConsumer(abc.PyDeviceStreamConsumer):
    bar: tqdm

    def __init__(
        self,
        on_description: Callable[[str, dict[str, Any] | None], tuple[str, dict[str, Any]]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._on_description = on_description or (
            lambda s, cfg: (
                s,
                cfg,
            )
        )

    def consumer(self, msg: str | bytes):
        if msg:
            _msg = msg if isinstance(msg, str) else msg.decode()
            self.on_message(_msg)

    def on_start(self, *, name: str = None, size: int | None = None):
        bar_format = "{l_bar}{bar}| [{n_fmt}/{total_fmt} @ {rate_fmt}]"
        tqdm_kwargs = {
            "unit_scale": True,
            "unit_divisor": 1024,
            "bar_format": bar_format,
        }
        _name, _tqdm_kws = self._on_description(name or "", tqdm_kwargs)
        self.bar = tqdm(total=size, unit="B", **(tqdm_kwargs | (_tqdm_kws or dict())))

    def on_update(self, *, size: int | None = None):
        self.bar.update(size)

    def on_end(self):
        self.bar.close()


def retry(fn: Callable[P, T]) -> Callable[P, T | None]:
    @wraps(fn)
    def _wrapper(self_: UPYPyDevice, *args: P.args, **kwargs: P.kwargs) -> T | None:
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


class UPYPyDevice(abc.PyDevice[AnyUPyDevice]):
    BUFFER_SIZE: int = BUFFER_SIZE

    _uos: UOS | None = None

    def _ensure_connected(self):
        if not self.connected:
            raise PyDeviceError(f"No currently connected device found!")

    def _rand_device_path(self) -> DevicePath:
        name = "".join(random.sample(string.ascii_lowercase, 6))
        return self._pyb_path(name)

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

    def _pyb_path(self, path: str) -> DevicePath:
        _root = PurePosixPath(self._pyb_root())
        _path = PurePosixPath(path)
        if _path.is_absolute():
            if _root == _path or _root in list(_path.parents):
                return DevicePath(str(_path))
            _path = _path.relative_to(list(_path.parents)[-1])
        return DevicePath(str(_root / _path))

    def establish(self, target: str) -> AnyUPyDevice:
        return upydevice.Device(target, init=True, autodetect=True)

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
        return False if self._pydevice is None else self._pydevice.connected

    def list_dir(self, path: DevicePath) -> list[DevicePath]:
        return [DevicePath(p) for p in self.uos.listdir(self._pyb_path(path))]

    def iter_files(self, path: DevicePath) -> Generator[DevicePath, None, None]:
        path = self._pyb_path(path)
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

    def copy_dir(self, source_path: DevicePath, target_path: HostPath):
        target_path = Path(target_path)
        source_path = self._pyb_path(source_path)
        for file_path in self.iter_files(source_path):
            rel_path = PurePosixPath(file_path).relative_to(
                list(PurePosixPath(file_path).parents)[-1]
            )
            file_dest = target_path / rel_path
            file_dest.parent.mkdir(parents=True, exist_ok=True)
            self.copy_file(file_path, file_dest)

    def copy_file(self, source_path: DevicePath, target_path: HostPath) -> None:
        source_path = self._pyb_path(source_path)
        target_path = Path(target_path)
        source_contents = self.read_file(source_path)
        if source_contents is None:
            # TODO: properly report failure to read/copy file.
            return None
        target_path.write_text(source_contents)

    def _iter_hex_chunks(self, content: str):
        chunked_content = iterutils.chunked_iter(content, self.BUFFER_SIZE)
        for chunk in chunked_content:
            hex_chunk = binascii.hexlify(chunk.encode())
            yield hex_chunk

    @retry
    def write_file(self, contents: str, target_path: DevicePath) -> None:
        target_path = self._pyb_path(target_path)
        self._pydevice.cmd("import ubinascii")
        self._pydevice.cmd(f"f = open('{str(target_path)}', 'wb')")
        content_size = len(binascii.hexlify(contents.encode())) // 2
        self._data_consumer.on_start(name=f"Writing {str(target_path)}", size=content_size)
        for chunk in self._iter_hex_chunks(contents):
            cmd = f"contents = ubinascii.unhexlify('{chunk.decode()}'); f.write(contents)"
            self._pydevice.cmd(cmd, silent=True)
            self._data_consumer.on_update(size=len(chunk) // 2)
        self._data_consumer.on_end()
        self._pydevice.cmd("f.close()")

    @retry
    def read_file(self, target_path: DevicePath) -> str:
        target_path = self._pyb_path(target_path)
        self._pydevice.cmd("import ubinascii", silent=True)
        self._pydevice.cmd(f"f = open('{str(target_path)}', 'rb')", silent=True)
        content_size = self._pydevice.cmd(f"f.seek(0,2)", rtn_resp=True, silent=True)
        self._pydevice.cmd("f.seek(0)", silent=True)
        buffer = io.BytesIO()
        self._data_consumer.on_start(name=f"Reading {target_path}", size=content_size // 2)
        last_pos = 0
        while True:
            pos = self._pydevice.cmd(f"f.tell()", rtn_resp=True, silent=True)
            self._data_consumer.on_update(size=(pos - last_pos) // 2)
            last_pos = pos
            if pos == content_size:
                self._data_consumer.on_end()
                break
            next_chunk = self._pydevice.cmd(
                f"f.read({self.BUFFER_SIZE})", rtn_resp=True, silent=True
            )
            buffer.write(next_chunk)
        self._pydevice.cmd("f.close()")
        value = buffer.getvalue().decode()
        return value

    def run_script(self, contents: str, target_path: DevicePath | None = None):
        target_path = (
            self._pyb_path(target_path) if target_path else f"{self._rand_device_path()}.py"
        )
        self.write_file(contents, target_path)
        self._pydevice.cmd(
            f"import {Path(target_path).stem}",
            follow=True,
            pipe=lambda m, *args, **kws: self._data_consumer.consumer(m),
        )
        self.uos.remove(str(target_path))
