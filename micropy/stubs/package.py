from __future__ import annotations

from pydantic import BaseModel


class StubPackage(BaseModel):
    class Config:
        frozen = True

    name: str
    version: str

    @property
    def package_name(self) -> str:
        return self.name
