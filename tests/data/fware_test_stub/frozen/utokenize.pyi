# make_stub_files: Thu 20 Jun 2019 at 23:08:04

from typing import Any, Dict, Optional, Sequence, Tuple, Union

Node = Any

class TokenInfo(namedtuple(str, Tuple[str, str, str, str, str])):
    def __str__(self) -> str: ...

def get_indent(l: Any) -> Tuple[int, Any]: ...
def tokenize(readline: Any) -> None: ...
