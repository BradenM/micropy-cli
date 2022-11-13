from __future__ import annotations

from pydantic import Field, validator
from typing_extensions import Annotated

from ..manifest import StubsManifest
from ..package import StubPackage


class MicropyStubPackage(StubPackage):
    name: str
    version: Annotated[str, Field(alias="sha256sum")]


class MicropyStubsManifest(StubsManifest):
    packages: list[MicropyStubPackage]

    @validator("packages", pre=True)
    def _get_packages(cls, v: dict[str, dict]):
        return v["packages"]
