from __future__ import annotations

from micropy.stubs import StubPackage, StubsManifest
from pydantic import BaseModel


class StubRepositoryPackage(BaseModel):
    manifest: StubsManifest
    package: StubPackage

    @property
    def url(self) -> str:
        return self.manifest.resolve_package_url(self.package)

    @property
    def repo_name(self) -> str:
        return self.manifest.repository.name

    @property
    def name(self) -> str:
        return self.package.name

    @property
    def version(self) -> str:
        return self.package.version

    @property
    def absolute_name(self) -> str:
        return self.manifest.resolve_package_absolute_name(self.package)

    @property
    def versioned_name(self) -> str:
        return self.manifest.resolve_package_versioned_name(self.package)

    @property
    def absolute_versioned_name(self) -> str:
        return self.manifest.resolve_package_absolute_versioned_name(self.package)

    def match_exact(self, in_name: str) -> bool:
        return in_name in [self.absolute_name, self.versioned_name, self.absolute_versioned_name]
