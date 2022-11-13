from __future__ import annotations

import abc
from pathlib import Path
from typing import Any, AnyStr

from typing_extensions import NewType, Protocol

HostPath = NewType("HostPath", str)
DevicePath = NewType("DevicePath", str)


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
    @property
    @abc.abstractmethod
    def on_start(self) -> StartHandler:
        ...

    @property
    @abc.abstractmethod
    def on_update(self) -> UpdateHandler:
        ...

    @property
    @abc.abstractmethod
    def on_end(self) -> EndHandler:
        ...


class MessageConsumer(Protocol):
    @property
    @abc.abstractmethod
    def on_message(self) -> MessageHandler:
        ...


class PyDeviceConsumer(MessageConsumer, StreamConsumer, Protocol):
    ...


class MetaPyDeviceBackend(abc.ABC):
    location: str

    @abc.abstractmethod
    def establish(self, target: str) -> MetaPyDeviceBackend:
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
    def resolve_path(self, target_path: DevicePath | str | Path) -> DevicePath:
        ...

    @property
    @abc.abstractmethod
    def connected(self) -> bool:
        ...

    @abc.abstractmethod
    def push_file(
        self,
        source_path: HostPath,
        target_path: DevicePath,
        *,
        consumer: PyDeviceConsumer | None,
        **kwargs,
    ) -> None:
        ...

    @abc.abstractmethod
    def pull_file(
        self,
        source_path: DevicePath,
        target_path: HostPath,
        *,
        consumer: PyDeviceConsumer | None,
        **kwargs,
    ) -> None:
        ...

    @abc.abstractmethod
    def list_dir(self, path: DevicePath) -> list[DevicePath]:
        ...

    @abc.abstractmethod
    def copy_dir(
        self,
        source_path: DevicePath,
        target_path: HostPath,
        *,
        consumer: PyDeviceConsumer | None,
        **kwargs,
    ):
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
        consumer: PyDeviceConsumer | None = None,
    ):
        ...


class MetaPyDevice(abc.ABC):
    pydevice: MetaPyDeviceBackend
    stream_consumer: StreamConsumer | None
    message_consumer: MessageConsumer | None

    @abc.abstractmethod
    def connect(self) -> None:
        ...

    @abc.abstractmethod
    def disconnect(self) -> None:
        ...

    @abc.abstractmethod
    def copy_to(self, source_path: HostPath, target_path: DevicePath) -> None:
        ...

    @abc.abstractmethod
    def copy_from(self, source_path: DevicePath, target_path: HostPath) -> None:
        ...

    @abc.abstractmethod
    def run_script(self, content: AnyStr, target_path: DevicePath | None = None):
        ...
