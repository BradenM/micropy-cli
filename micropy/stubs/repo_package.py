from __future__ import annotations

from micropy.stubs import StubPackage, StubsManifest
from pydantic import BaseModel


class StubRepositoryPackage(BaseModel):
    repository: StubsManifest
    package: StubPackage

    @property
    def url(self) -> str:
        return self.repository.resolve_package_url(self.package)
