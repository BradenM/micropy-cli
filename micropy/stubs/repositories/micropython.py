from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from distlib.locators import locate
from distlib.version import NormalizedVersion
from pydantic import Field, validator
from typing_extensions import Annotated

from ..manifest import StubsManifest
from ..package import StubPackage

if TYPE_CHECKING:
    from distlib.database import Distribution


@functools.total_ordering
class MicropythonStubsPackage(StubPackage):
    name: str
    version: Annotated[str, Field(alias="pkg_version")]

    @property
    def package_version(self) -> NormalizedVersion:
        return NormalizedVersion(self.version)

    def __lt__(self, other: MicropythonStubsPackage) -> bool:
        return self.package_version < other.package_version

    def __eq__(self, other: MicropythonStubsPackage) -> bool:
        return self.name == other.name and self.version == other.version


class MicropythonStubsManifest(StubsManifest[MicropythonStubsPackage]):
    @validator("packages", pre=True)
    def _get_packages(cls, v: dict[str, dict]):
        data = v["data"].values()
        return list(data)

    def resolve_package_url(self, package: StubPackage) -> str:
        dist: Distribution = locate(f"{package.name} ({package.version})")
        dist_url = next(i for i in dist.download_urls if "tar.gz" in i)
        return dist_url
