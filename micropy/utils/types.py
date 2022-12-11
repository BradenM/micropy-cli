"""Type utilities and variables."""

from __future__ import annotations

from os import PathLike
from typing import Any, Union

from typing_extensions import Protocol, TypeAlias, runtime_checkable

# PathLike string or string type alias.
PathStr: TypeAlias = Union[str, PathLike]


@runtime_checkable
class SupportsLessThan(Protocol):
    def __lt__(self, other: Any) -> bool:
        ...
