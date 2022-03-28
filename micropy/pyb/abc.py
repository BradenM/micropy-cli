from __future__ import annotations

import abc
from typing import Any, AnyStr, NewType, TypeVar

from typing_extensions import Protocol

HostPath = NewType("HostPath", str)
DevicePath = NewType("DevicePath", str)

DeviceT = TypeVar("DeviceT")


class StartHandler(Protocol):
    def __call__(self, *, name: str = None, size: int | None = None) -> Any:
        ...


class UpdateHandler(Protocol):
    def __call__(self, *, size: int | None = None) -> Any:
        ...


class EndHandler(Protocol):
    def __call__(self) -> Any:
        ...


class MessageHandler(Protocol):
    def __call__(self, data: AnyStr) -> Any:
        ...


class StreamConsumer(Protocol):
    on_start: StartHandler
    on_update: UpdateHandler
    on_end: EndHandler


class MessageConsumer(Protocol):
    on_message: MessageHandler


AnyPyDevice = TypeVar("AnyPyDevice", bound="MetaPyDeviceBackend")


class MetaPyDeviceBackend(abc.ABC):
    location: str

    @abc.abstractmethod
    def establish(self, target: str) -> AnyPyDevice:
        ...

    @abc.abstractmethod
    def connect(self) -> None:
        ...

    @abc.abstractmethod
    def disconnect(self) -> None:
        ...

    @abc.abstractmethod
    def reset(self) -> None:
        ...

    @abc.abstractmethod
    def resolve_path(self, target_path: DevicePath) -> DevicePath:
        ...

    @property
    @abc.abstractmethod
    def connected(self) -> bool:
        ...

    @abc.abstractmethod
    def push_file(self, source_path: HostPath, target_path: DevicePath, **kwargs) -> None:
        ...

    @abc.abstractmethod
    def pull_file(self, source_path: DevicePath, target_path: HostPath, **kwargs) -> None:
        ...

    @abc.abstractmethod
    def list_dir(self, path: DevicePath) -> list[DevicePath]:
        ...

    @abc.abstractmethod
    def copy_dir(self, source_path: DevicePath, target_path: HostPath, **kwargs):
        ...

    @abc.abstractmethod
    def eval(self, command: str, *, consumer: MessageConsumer | None = None):
        ...

    @abc.abstractmethod
    def eval_script(
        self,
        contents: AnyStr,
        target_path: DevicePath | None = None,
        *,
        stream_consumer: StreamConsumer = None,
        message_consumer: MessageConsumer | None = None,
    ):
        ...


class MetaPyDevice(abc.ABC):
    pydevice: MetaPyDeviceBackend
    stream_consumer: StreamConsumer | None
    message_consumer: MessageConsumer | None

    @abc.abstractmethod
    def copy_to(self, source_path: HostPath, target_path: DevicePath) -> None:
        ...

    @abc.abstractmethod
    def copy_from(self, source_path: DevicePath, target_path: HostPath) -> None:
        ...

    @abc.abstractmethod
    def run_script(self, content: AnyStr, target_path: DevicePath | None = None):
        ...
