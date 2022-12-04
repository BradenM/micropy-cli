from __future__ import annotations

from datetime import timedelta
from typing import Any

import requests
from cachier import cachier
from pydantic import BaseModel, HttpUrl


class RepositoryInfo(BaseModel):
    name: str
    display_name: str
    source: HttpUrl

    class Config:
        frozen = True

    @cachier(stale_after=timedelta(days=1), next_time=True)
    def fetch_source(self) -> dict[str, Any]:
        return requests.get(self.source).json()
