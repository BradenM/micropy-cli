from __future__ import annotations

from typing import ClassVar

from micropy.stubs.package import StubPackage
from micropy.stubs.repository_info import RepositoryInfo
from pydantic import BaseModel


class StubsManifest(BaseModel):
    manifest_formats: ClassVar[list[type[StubsManifest]]] = []

    repository: RepositoryInfo
    packages: list[StubPackage]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.manifest_formats.append(cls)
