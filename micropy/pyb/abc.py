from __future__ import annotations

import abc
from typing import Any, AnyStr, Callable, Generic, NewType, TypeVar

HostPath = NewType("HostPath", str)
DevicePath = NewType("DevicePath", str)

DeviceT = TypeVar("DeviceT")


class PyDeviceConsumer(abc.ABC):
    def __init__(self, on_message: Callable[[str], Any]):
        self.on_message = on_message

    @abc.abstractmethod
    def consumer(self, data: bytes | str) -> None:
        raise NotImplementedError


class PyDeviceStreamConsumer(PyDeviceConsumer, abc.ABC):
    @abc.abstractmethod
    def on_start(self, *, name: str = None, size: int | None = None):
        raise NotImplementedError()

    @abc.abstractmethod
    def on_update(self, *, size: int | None = None):
        raise NotImplementedError()

    @abc.abstractmethod
    def on_end(self):
        raise NotImplementedError()


class NoOpStreamConsumer(PyDeviceStreamConsumer):
    def __init__(self):
        super().__init__(on_message=lambda *a, **k: None)

    def on_start(self, *, name: str = None, size: int | None = None):
        pass

    def on_update(self, *, size: int | None = None):
        pass

    def on_end(self):
        pass

    def consumer(self, data: bytes | str) -> None:
        pass


class MetaPyDevice(abc.ABC):
    @abc.abstractmethod
    def copy_file(self, source_path: HostPath, target_path: DevicePath) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def list_dir(self, path: DevicePath) -> list[DevicePath]:
        raise NotImplementedError()

    @abc.abstractmethod
    def copy_dir(self, source_path: DevicePath, target_path: HostPath):
        raise NotImplementedError()

    @abc.abstractmethod
    def run_script(self, content: HostPath | AnyStr, target_path: DevicePath | None = None):
        raise NotImplementedError()


class MetaDeviceBackend(Generic[DeviceT], abc.ABC):
    @abc.abstractmethod
    def establish(self, target: str) -> DeviceT | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def connect(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def disconnect(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def reset(self):
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def connected(self) -> bool:
        raise NotImplementedError()


class PyDevice(Generic[DeviceT], MetaPyDevice, MetaDeviceBackend[DeviceT], abc.ABC):
    _location: str
    _pydevice: DeviceT
    _data_consumer: PyDeviceConsumer | PyDeviceStreamConsumer

    def __init__(
        self,
        location: str,
        auto_connect: bool = True,
        data_consumer: PyDeviceConsumer | PyDeviceStreamConsumer | None = None,
    ):
        self._location = location
        # TODO: can use walrus (:=) here when 3.7 support is dropped.
        pyd = self.establish(self._location)
        if pyd is not None:
            self._pydevice = pyd
        self._data_consumer = data_consumer or NoOpStreamConsumer()
        if auto_connect:
            self.connect()

    @property
    def location(self) -> str:
        return self._location
