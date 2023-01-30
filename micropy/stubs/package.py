from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel


class StubPackage(BaseModel):
    class Config:
        frozen = True
        allow_population_by_field_name = True

    name: str
    version: str

    @property
    def package_name(self) -> str:
        return self.name


AnyStubPackage = TypeVar("AnyStubPackage", bound=StubPackage)
