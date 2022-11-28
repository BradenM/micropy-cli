from __future__ import annotations

from typing import TYPE_CHECKING

from distlib.locators import locate
from pydantic import Field, validator
from typing_extensions import Annotated

from ..manifest import StubsManifest
from ..package import StubPackage

if TYPE_CHECKING:
    from distlib.database import Distribution


class MicropythonStubsPackage(StubPackage):
    name: str
    version: Annotated[str, Field(alias="pkg_version")]


class MicropythonStubsManifest(StubsManifest):

    packages: list[MicropythonStubsPackage]

    @validator("packages", pre=True)
    def _get_packages(cls, v: dict[str, dict]):
        data = v["data"].values()
        return list(data)

    def resolve_package_url(self, package: StubPackage) -> str:
        dist: Distribution = locate(f"{package.name} ({package.version})")
        dist_url = next(i for i in dist.download_urls if "tar.gz" in i)
        return dist_url
