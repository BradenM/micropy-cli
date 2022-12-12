from __future__ import annotations

import collections
import inspect
from typing import TYPE_CHECKING, ClassVar, Generator, Iterator, Optional, Type

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

    packages_index: collections.ChainMap[str, StubRepositoryPackage] = attrs.field(
        factory=collections.ChainMap
    )
    versions_index: collections.ChainMap[str, list[StubRepositoryPackage]] = attrs.field(
        factory=collections.ChainMap
    )

    manifest_types: ClassVar[list[Type[StubsManifest]]] = []

    def __attrs_post_init__(self) -> None:
        if not any(StubRepository.manifest_types):
            StubRepository.manifest_types = [
                klass
                for klass in get_all_subclasses(StubsManifest)
                if not inspect.isabstract(klass)
            ]
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
            packages_index = dict()
            versions_index = collections.defaultdict(list)
            for package in manifest.packages:
                repo_package = StubRepositoryPackage(manifest=manifest, package=package)
                packages_index[repo_package.absolute_versioned_name] = repo_package
                versions_index[repo_package.name].append(repo_package)

            self.packages_index = self.packages_index.new_child(packages_index)
            self.versions_index = self.versions_index.new_child(dict(versions_index))

    def add_repository(self, info: RepositoryInfo) -> StubRepository:
        """Creates a new `StubRepository` instance with a `StubManifest` derived from `info`.

        Args:
            info: `RepositoryInfo` instance.

        Returns:
            `StubRepository` instance.

        """
        contents = info.fetch_source()
        data = dict(repository=info, packages=contents)
        for manifest_type in StubRepository.manifest_types:
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

    def search(
        self, query: str, include_versions: bool = True
    ) -> Generator[StubRepositoryPackage, None, None]:
        """Search packages for `query`.

        Args:
            query: Search constraint.
            include_versions: Whether to include versions in search results.

        Returns:
            A generator of `StubRepositoryPackage` objects.

        """
        query = query.strip().lower()
        for package_name in self.versions_index.keys():
            if query in package_name.lower() or package_name.lower() in query:
                if include_versions:
                    yield from self.versions_index[package_name]
                    continue
                yield self.latest_for_package(self.versions_index[package_name][0])

    def latest_for_package(
        self, repo_package: StubRepositoryPackage
    ) -> Optional[StubRepositoryPackage]:
        versions = self.versions_index[repo_package.name]
        if len(versions) == 1:
            return versions[0]
        return max(versions, key=lambda x: x.package.version)

    def resolve_package(self, name: str) -> StubRepositoryPackage:
        """Resolve a package name to a package path.

        Args:
            name: Package name.

        Returns:
            Package location.

        Throws:
            StubNotFound: When package cannot be resolved.

        """
        for package in self.search(str(name)):
            if package.match_exact(name) or package.match_exact(
                "/".join([package.repo_name, name])
            ):
                return package
            latest = self.latest_for_package(package)
            if latest and latest.name == name:
                return latest
        raise exc.StubNotFound(name)
