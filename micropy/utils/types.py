"""Type utilities and variables."""

from os import PathLike
from typing import Union

from typing_extensions import TypeAlias

PathStr: TypeAlias = Union[str, PathLike[str]]
