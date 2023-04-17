from __future__ import annotations

import binascii
import hashlib
import io
import random
import stat
import string
import time
from functools import wraps
from pathlib import Path, PurePosixPath
from typing import AnyStr, Callable, Generator, Optional, TypeVar, Union

import upydevice
from boltons import iterutils
from micropy.exceptions import PyDeviceConnectionError, PyDeviceError, PyDeviceFileIntegrityError
from rich import print
from typing_extensions import ParamSpec, TypeAlias
from upydevice.phantom import UOS as UPY_UOS

from .abc import DevicePath, HostPath, MessageConsumer, MetaPyDeviceBackend, PyDeviceConsumer
from .consumers import NoOpConsumer

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
                if (integrity := kwargs.pop("verify_integrity", None)) is not None:
                    # skip integrity check on last retry as last ditch.
                    kwargs["verify_integrity"] = integrity and retry_count < 3
                    if integrity and not kwargs["verify_integrity"]:
                        print("Attempting again without file integrity check...")
                _result = fn(self_, *args, **kwargs)  # type: ignore
            except PyDeviceFileIntegrityError as e:
                retry_count += 1
                print(e)
                self_.reset()
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
            raise PyDeviceError("No currently connected device found!")

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
        for file_result in results:
            name, type_, _, _ = file_result
            abs_path = PurePosixPath(path) / name
            if type_ == stat.S_IFDIR:
                yield from self.iter_files(abs_path)
            else:
                yield abs_path

    def copy_dir(
        self,
        source_path: DevicePath,
        target_path: HostPath,
        exclude_integrity: Optional[set[str]] = None,
        **kwargs,
    ):
        target_path = Path(str(target_path))  # type: ignore
        source_path = self.resolve_path(source_path)
        exclude_integrity = exclude_integrity or set()
        for file_path in self.iter_files(source_path):
            rel_path = PurePosixPath(file_path).relative_to(
                list(PurePosixPath(file_path).parents)[-1]
            )
            # handles os-path conversion
            file_dest = Path(target_path / rel_path)
            file_dest.parent.mkdir(parents=True, exist_ok=True)
            integ_exclude = (
                file_path in exclude_integrity or Path(file_path).name in exclude_integrity
            )
            integrity = kwargs.pop("verify_integrity", True) and not integ_exclude
            self.pull_file(
                file_path, HostPath(str(file_dest)), verify_integrity=integrity, **kwargs
            )

    def push_file(
        self, source_path: HostPath, target_path: DevicePath, binary: bool = False, **kwargs
    ) -> None:
        src_path = Path(str(source_path))
        src_contents = src_path.read_bytes() if binary else src_path.read_text()
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
        self,
        contents: str | bytes,
        target_path: DevicePath,
        *,
        consumer: PyDeviceConsumer = NoOpConsumer,
    ) -> None:
        is_bytes = isinstance(contents, bytes)
        target_path = self.resolve_path(target_path)
        self._pydevice.cmd("import gc")
        self._pydevice.cmd("import ubinascii")
        self._pydevice.cmd(f"f = open('{str(target_path)}', 'wb')")

        content_iter = (
            iterutils.chunked_iter(contents, self.BUFFER_SIZE)
            if is_bytes
            else self._iter_hex_chunks(contents)
        )

        content_size = len(contents)
        consumer.on_start(name=f"Writing {str(target_path)}", size=content_size)

        for chunk in content_iter:
            cmd = (
                f"contents = {chunk}; f.write(contents)"
                if is_bytes
                else f"contents = ubinascii.unhexlify('{chunk.decode()}'); f.write(contents)"
            )
            self._pydevice.cmd(cmd, silent=True)
            consumer.on_update(size=len(chunk))
        consumer.on_end()
        self._pydevice.cmd("f.close()")
        self._pydevice.cmd("import gc; gc.collect()")

    def _compute_chunk_size(self) -> int:
        mem_free = int(
            self._pydevice.cmd("import gc;_=gc.collect();gc.mem_free()", rtn_resp=True, silent=True)
        )
        return min(mem_free // 4, 4096)

    def _compute_device_file_digest(
        self,
        device_path: DevicePath,
        *,
        chunk_size: int = 256,
        content_size: Optional[int] = None,
        pos: int = 0,
    ) -> str:
        checksum_cmd = ";".join(
            [
                "import ubinascii, uhashlib, gc",
                "f=open('{path}', 'rb')",
                "sha = uhashlib.sha256()",
                "__=[sha.update(f.read({chunk_size})) and gc.collect() for _ in range({pos}, {file_size}, {chunk_size})]",
                "ubinascii.hexlify(sha.digest()).decode()",
            ]
        )
        if content_size is None:
            content_size = self.uos.stat(str(device_path))[6]
        sum_cmd = checksum_cmd.format(
            path=str(device_path), chunk_size=chunk_size, file_size=content_size, pos=pos
        )
        return self._pydevice.cmd(sum_cmd, silent=True, rtn_resp=True)

    @retry
    def read_file(
        self,
        target_path: DevicePath,
        *,
        consumer: PyDeviceConsumer = NoOpConsumer,
        verify_integrity: bool = True,
    ) -> str:
        target_path = self.resolve_path(target_path)

        read_chunk_cmd = (
            "f=open('{path}', 'rb');_=f.seek({pos});ch=f.read({chunk_size});f.close();ch"
        )

        content_size = self.uos.stat(str(target_path))[6]
        buffer = io.BytesIO()
        pos = 0
        chunk_size = self._compute_chunk_size()
        consumer.on_start(
            name=f"Reading {Path(target_path).name} (xsize: {chunk_size})", size=int(content_size)
        )
        hasher = hashlib.sha256()
        while pos < content_size:
            try:
                cmd = read_chunk_cmd.format(path=str(target_path), pos=pos, chunk_size=chunk_size)
                next_chunk = self._pydevice.cmd(cmd, rtn_resp=True, silent=True)
            except Exception as e:
                consumer.on_message(f"Failed to read chunk; retrying ({e})")
                self.reset()
                chunk_size = self._compute_chunk_size()
                continue
            if len(next_chunk) == 0:
                consumer.on_message("Failed to read chunk (no data); retrying.")
                self.reset()
                continue
            hasher.update(next_chunk)
            buffer.write(next_chunk)
            pos += chunk_size
            consumer.on_update(size=len(next_chunk))
        consumer.on_end()

        if verify_integrity:
            device_sum = self._compute_device_file_digest(
                target_path, chunk_size=chunk_size, content_size=content_size, pos=0
            )
            digest = hasher.hexdigest()
            if device_sum != digest:
                raise PyDeviceFileIntegrityError(
                    device_path=Path(target_path).name, device_sum=device_sum, digest=digest
                )
            consumer.on_message(f"Verified integrity: {Path(target_path).name}")

        value = buffer.getvalue().decode()
        return value

    def eval(self, command: str, *, consumer: MessageConsumer = NoOpConsumer) -> str | None:
        return self._pydevice.cmd(
            command, follow=True, pipe=lambda m, *args, **kws: consumer.on_message(m)
        )

    def eval_script(
        self,
        contents: AnyStr,
        target_path: DevicePath | None = None,
        *,
        consumer: PyDeviceConsumer = NoOpConsumer,
    ):
        _target_path = (
            self.resolve_path(target_path) if target_path else f"{self._rand_device_path()}.py"
        )
        self.write_file(contents, DevicePath(_target_path), consumer=consumer)
        self.eval(f"import {Path(_target_path).stem}", consumer=consumer)
        self.uos.remove(str(_target_path))

    def remove(self, path: DevicePath) -> None:
        self.uos.remove(str(path))
