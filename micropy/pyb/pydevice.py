from __future__ import annotations

from pathlib import Path
from typing import AnyStr, Type

from .abc import (
    DevicePath,
    HostPath,
    MessageConsumer,
    MetaPyDevice,
    MetaPyDeviceBackend,
    StreamConsumer,
)
from .backend_upydevice import UPyDeviceBackend


class PyDevice(MetaPyDevice):
    stream_consumer: StreamConsumer
    message_consumer: MessageConsumer

    def __init__(
        self,
        location: str,
        *,
        backend: Type[MetaPyDeviceBackend] = UPyDeviceBackend,
        auto_connect: bool = True,
        stream_consumer: StreamConsumer = None,
        message_consumer: MessageConsumer = None,
    ):
        self.pydevice = backend().establish(location)
        self.stream_consumer = stream_consumer
        self.message_consumer = message_consumer
        if auto_connect:
            self.pydevice.connect()

    def copy_from(self, source_path: DevicePath, target_path: HostPath) -> None:
        src_path = Path(str(source_path))
        if src_path.is_dir():
            return self.pydevice.copy_dir(source_path, target_path)
        return self.pydevice.pull_file(source_path, target_path)

    def copy_to(self, source_path: HostPath, target_path: DevicePath) -> None:
        src_path = Path(str(source_path))
        if src_path.is_dir():
            raise RuntimeError("Copying dirs to device is not yet supported!")
        return self.pydevice.push_file(source_path, target_path)

    def run_script(self, content: AnyStr, target_path: DevicePath | None = None):
        return self.pydevice.eval_script(
            contents,
            target_path,
            stream_consumer=self.stream_consumer,
            message_consumer=self.message_consumer,
        )
