from __future__ import annotations

import collections
from collections import defaultdict
from typing import TYPE_CHECKING, Generator, Iterator

import attrs
import micropy.exceptions as exc
from boltons.typeutils import get_all_subclasses

from .manifest import StubsManifest
from .repo_package import StubRepositoryPackage

if TYPE_CHECKING:
    from .repository_info import RepositoryInfo


@attrs.define
class StubRepository:
    manifests: list[StubsManifest] = attrs.field(factory=list)

    packages_index: dict[str, StubRepositoryPackage] = attrs.field(factory=dict)
    versions_index: defaultdict[str, list[StubRepositoryPackage]] = attrs.field(
        factory=lambda: collections.defaultdict(list)
    )

    def __attrs_post_init__(self) -> None:
        self.build_indexes()

    @property
    def packages(self) -> Iterator[StubRepositoryPackage]:
        """Iterate packages in repository."""
        yield from self.packages_index.values()

    def build_indexes(self) -> None:
        """Progressively builds indexes."""
        for manifest in self.manifests:
            pkg = next(iter(manifest.packages), None)
            if pkg and manifest.resolve_package_absolute_versioned_name(pkg) in self.packages_index:
                continue
            for package in manifest.packages:
                repo_package = StubRepositoryPackage(manifest=manifest, package=package)
                self.packages_index[repo_package.absolute_versioned_name] = repo_package
                self.versions_index[repo_package.absolute_name].append(repo_package)

    def add_repository(self, info: RepositoryInfo) -> StubRepository:
        """Creates a new `StubRepository` instance with a `StubManifest` derived from `info`.

        Args:
            info: `RepositoryInfo` instance.

        Returns:
            `StubRepository` instance.

        """
        contents = info.fetch_source()
        data = dict(repository=info, packages=contents)
        for manifest_type in get_all_subclasses(StubsManifest):
            try:
                manifest = manifest_type.parse_obj(data)
            except (
                ValueError,
                KeyError,
            ):
                continue
            else:
                return attrs.evolve(
                    self,
                    manifests=self.manifests + [manifest],
                    packages_index=self.packages_index,
                    versions_index=self.versions_index,
                )
        raise ValueError(f"Failed to determine manifest format for repo: {info}")

    def search(self, query: str) -> Generator[StubRepositoryPackage, None, None]:
        """Search packages for `query`.

        Args:
            query: Search constraint.

        Returns:
            A generator of `StubRepositoryPackage` objects.

        """
        query = query.strip().lower()
        for package_name in self.versions_index:
            if query in package_name.lower() or package_name.lower() in query:
                yield from self.versions_index[package_name]

    def resolve_package(self, name: str) -> str:
        """Resolve a package name to a package path.

        Args:
            name: Package name.

        Returns:
            Package location.

        Throws:
            StubNotFound: When package cannot be resolved.

        """
        for package in self.search(name):
            if package.match_exact(name):
                return package.url
        raise exc.StubNotFound(name)
