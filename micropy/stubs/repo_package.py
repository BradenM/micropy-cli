from __future__ import annotations

from micropy.stubs import StubPackage, StubsManifest
from pydantic import BaseModel


class StubRepositoryPackage(BaseModel):
    repository: StubsManifest
    package: StubPackage
