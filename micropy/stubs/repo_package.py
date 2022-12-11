from __future__ import annotations

from typing import Iterator

import attrs
from micropy.stubs import StubPackage, StubsManifest


@attrs.frozen
class StubRepositoryPackage:
    manifest: StubsManifest[StubPackage]
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

    @property
    def exact_matchers(self) -> Iterator[str]:
        yield self.absolute_versioned_name
        yield self.versioned_name
        yield self.absolute_name

    @property
    def partial_matchers(self) -> Iterator[str]:
        yield from self.exact_matchers
        yield self.name
        yield self.version

    def match_exact(self, in_name: str) -> bool:
        return in_name in self.exact_matchers
