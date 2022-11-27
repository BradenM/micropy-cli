from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import attrs
import micropy.exceptions as exc
import requests

from .manifest import StubsManifest
from .repo_package import StubRepositoryPackage

if TYPE_CHECKING:
    from .repository_info import RepositoryInfo


@attrs.define
class StubRepository:
    manifests: list[StubsManifest] = attrs.field(factory=list)
    packages: list[StubRepositoryPackage] = attrs.field(factory=list)

    def __attrs_post_init__(self):
        self._build_packages()

    def _build_packages(self) -> None:
        for manifest in self.manifests:
            for package in manifest.packages:
                self.packages.append(StubRepositoryPackage(repository=manifest, package=package))

    def add_repository(self, info: RepositoryInfo) -> StubRepository:
        """Creates a new `StubRepository` instance with a `StubManifest` derived from `info`.

        Args:
            info: `RepositoryInfo` instance.

        Returns:
            `StubRepository` instance.

        """
        contents = requests.get(info.source).json()
        data = dict(repository=info, packages=contents)
        for manifest_type in StubsManifest.manifest_formats:
            try:
                manifest = manifest_type.parse_obj(data)
            except (
                ValueError,
                KeyError,
            ):
                continue
            else:
                return StubRepository(manifests=[*self.manifests, manifest])
        raise ValueError(f"Failed to determine manifest format for repo: {info}")

    def search(self, query: str) -> Generator[StubRepositoryPackage, None, None]:
        """Search packages for `query`.

        Args:
            query: Search constraint.

        Returns:
            A generator of `StubRepositoryPackage` objects.

        """
        query = query.strip().lower()
        for package in self.packages:
            if query in package.package.name.lower():
                yield package

    def resolve_package(self, name: str) -> str:
        pkg = next((p for p in self.packages if p.package.name == name), None)
        if pkg is None:
            raise exc.StubNotFound(pkg)
        return pkg.url
