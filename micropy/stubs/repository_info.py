from __future__ import annotations

from pydantic import BaseModel


class RepositoryInfo(BaseModel):
    name: str
    display_name: str
    source: str
