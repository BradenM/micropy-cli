from __future__ import annotations

from micropy.stubs import StubPackage, StubsManifest
from pydantic import BaseModel


class StubRepositoryPackage(BaseModel):
    repository: StubsManifest
    package: StubPackage

    @property
    def url(self) -> str:
        return self.repository.resolve_package_url(self.package)

    @property
    def name(self) -> str:
        return self.package.name

    @property
    def version(self) -> str:
        return self.package.version

    @property
    def absolute_name(self) -> str:
        return self.repository.resolve_package_absolute_name(self.package)
