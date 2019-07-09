# make_stub_files: Thu 20 Jun 2019 at 23:08:04

from typing import Any, Dict, Optional, Sequence, Tuple, Union
Node = Any
def roundup(val: Any, align: Any) -> Any: ...
    #   0: return val+align-1&~align-1
    # ? 0: return val+align-number&align-number
class FileSection:
    def __init__(self, f: Any, content_len: smallint, aligned_len: smallint) -> None: ...
    def read(self, sz: Any=65536) -> Union[Any, bytes]: ...
        #   0: return b''
        #   0: return bytes
        #   1: return data
        # ? 1: return data
    def readinto(self, buf: Any) -> Union[Any, number]: ...
        #   0: return 0
        #   0: return number
        #   1: return sz
        # ? 1: return sz
    def skip(self) -> None: ...
class TarInfo:
    def __str__(self) -> str: ...
class TarFile:
    def __init__(self, name: str=None, fileobj: Any=None) -> None: ...
    def next(self) -> Optional[Any]: ...
        #   0: return None
        #   0: return None
        #   1: return None
        #   1: return None
        #   2: return d
        # ? 2: return d
    def __iter__(self) -> Any: ...
        #   0: return self
        # ? 0: return self
    def __next__(self) -> Any: ...
        #   0: return v
        # ? 0: return v
    def extractfile(self, tarinfo: Any) -> Any: ...
        #   0: return tarinfo.subf
        # ? 0: return tarinfo.subf
