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
from .consumers import ConsumerDelegate


class PyDevice(MetaPyDevice):
    pydevice: MetaPyDeviceBackend
    consumer: ConsumerDelegate

    def __init__(
        self,
        location: str,
        *,
        backend: Type[MetaPyDeviceBackend] = UPyDeviceBackend,
        auto_connect: bool = True,
        stream_consumer: StreamConsumer = None,
        message_consumer: MessageConsumer = None,
        delegate_cls: Type[ConsumerDelegate] = ConsumerDelegate,
    ):
        self.pydevice = backend().establish(location)
        self.consumer = delegate_cls(stream_consumer, message_consumer)
        if auto_connect and self.pydevice:
            self.pydevice.connect()

    def copy_from(self, source_path: DevicePath, target_path: HostPath) -> None:
        src_path = Path(str(source_path))
        # 'is_dir/file' only works on existing paths.
        if not src_path.suffix:
            return self.pydevice.copy_dir(
                DevicePath(source_path), target_path, consumer=self.consumer
            )
        return self.pydevice.pull_file(DevicePath(source_path), target_path, consumer=self.consumer)

    def copy_to(self, source_path: HostPath, target_path: DevicePath) -> None:
        src_path = Path(str(source_path))
        host_exists = src_path.exists()
        if (host_exists and src_path.is_dir()) or (not host_exists and not src_path.suffix):
            raise RuntimeError("Copying dirs to device is not yet supported!")
        return self.pydevice.push_file(source_path, target_path, consumer=self.consumer)

    def connect(self):
        return self.pydevice.connect()

    def disconnect(self):
        return self.pydevice.disconnect()

    def run_script(self, content: AnyStr, target_path: DevicePath | None = None):
        return self.pydevice.eval_script(content, target_path, consumer=self.consumer)
