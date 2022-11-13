from __future__ import annotations

from pydantic import BaseModel


class RepositoryInfo(BaseModel):
    name: str
    source: str
