from __future__ import annotations

from io import BytesIO, StringIO
from pathlib import Path
from typing import AnyStr, Generic, Optional, Type

from .abc import (
    AnyBackend,
    DevicePath,
    HostPath,
    MessageConsumer,
    MetaPyDevice,
    MetaPyDeviceBackend,
    StreamConsumer,
)
from .backend_upydevice import UPyDeviceBackend
from .consumers import ConsumerDelegate


class PyDevice(MetaPyDevice[AnyBackend], Generic[AnyBackend]):
    pydevice: AnyBackend
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

    def copy_from(
        self,
        source_path: DevicePath,
        target_path: HostPath,
        *,
        verify_integrity: bool = True,
        exclude_integrity: Optional[set[str]] = None,
    ) -> None:
        src_path = Path(str(source_path))
        # 'is_dir/file' only works on existing paths.
        if not src_path.suffix:
            return self.pydevice.copy_dir(
                DevicePath(source_path),
                target_path,
                consumer=self.consumer,
                verify_integrity=verify_integrity,
                exclude_integrity=exclude_integrity,
            )
        return self.pydevice.pull_file(
            DevicePath(source_path),
            target_path,
            consumer=self.consumer,
            verify_integrity=verify_integrity,
        )

    def copy_to(self, source_path: HostPath, target_path: DevicePath, **kwargs) -> None:
        src_path = Path(str(source_path))
        host_exists = src_path.exists()
        if (host_exists and src_path.is_dir()) or (not host_exists and not src_path.suffix):
            raise RuntimeError("Copying dirs to device is not yet supported!")
        return self.pydevice.push_file(source_path, target_path, consumer=self.consumer, **kwargs)

    def remove(self, target_path: DevicePath) -> None:
        return self.pydevice.remove(target_path)

    def connect(self):
        return self.pydevice.connect()

    def disconnect(self):
        return self.pydevice.disconnect()

    def run_script(
        self, content: AnyStr | StringIO | BytesIO, target_path: DevicePath | None = None
    ):
        _content = (
            content
            if isinstance(
                content,
                (
                    str,
                    bytes,
                ),
            )
            else content.read()
        )
        return self.pydevice.eval_script(_content, target_path, consumer=self.consumer)

    def run(self, content: str) -> str | None:
        return self.pydevice.eval(content, consumer=self.consumer)
