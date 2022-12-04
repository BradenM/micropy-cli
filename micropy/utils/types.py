"""Type utilities and variables."""

from os import PathLike
from typing import Union

from typing_extensions import TypeAlias

# PathLike string or string type alias.
PathStr: TypeAlias = Union[str, PathLike[str]]
