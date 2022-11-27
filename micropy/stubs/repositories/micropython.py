from __future__ import annotations

from pydantic import Field, validator
from typing_extensions import Annotated

from ..manifest import StubsManifest
from ..package import StubPackage


class MicropythonStubsPackage(StubPackage):
    name: str
    version: Annotated[str, Field(alias="pkg_version")]

    @property
    def package_name(self) -> str:
        return f"{self.name}@{self.version}"


class MicropythonStubsManifest(StubsManifest):

    packages: list[MicropythonStubsPackage]

    @validator("packages", pre=True)
    def _get_packages(cls, v: dict[str, dict]):
        data = v["data"].values()
        return list(data)

    def resolve_package_url(self, package: StubPackage) -> str:
        pass
