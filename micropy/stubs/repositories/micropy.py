from __future__ import annotations

from pathlib import PurePosixPath
from urllib import parse

from pydantic import Field, root_validator
from typing_extensions import Annotated

from ..manifest import StubsManifest
from ..package import StubPackage


class MicropyStubPackage(StubPackage):
    name: str
    version: Annotated[str, Field(alias="sha256sum")]


class MicropyStubsManifest(StubsManifest[MicropyStubPackage]):
    location: str
    path: str

    @root_validator(pre=True)
    def check(cls, values: dict):
        pkgs = values["packages"]
        if "packages" in pkgs:
            values["location"] = pkgs["location"]
            values["path"] = pkgs["path"]
            values["packages"] = pkgs["packages"]
        return values

    def resolve_package_url(self, package: StubPackage) -> str:
        base_path = PurePosixPath(parse.urlparse(self.location).path)
        pkg_path = base_path / PurePosixPath(self.path) / PurePosixPath(package.name)
        url = parse.urljoin(self.location, str(pkg_path))
        return url
