# -*- coding: utf-8 -*-


from pathlib import Path
from typing import List, Optional, Tuple

import requirements
from packaging.utils import canonicalize_name


class Package:

    def __init__(
            self, name: str, specs: List[Tuple[str, str]],
            path: Optional[Path] = None, uri: Optional[str] = None, vcs: Optional[str] = None,
            revision: Optional[str] = None, line: Optional[str] = None, **kwargs):
        """Generic Python Dependency.

        Args:
            name (str): Name of package
            specs (List[Tuple[str, str]]): Package constraints.
            path: path to package

        """
        self._name = name
        self._specs = specs
        self._path = path
        self._uri = uri
        self._vcs = vcs
        self._revision = revision
        self._line = line
        self.editable = (self._path is not None)

    @property
    def name(self) -> str:
        return canonicalize_name(self._name)

    @property
    def path(self) -> Optional[Path]:
        if not self._path:
            return None
        return Path(self._path)

    @property
    def full_name(self) -> str:
        if self._line and self._vcs:
            return self._line
        if self._path:
            return self.pretty_specs
        if not self._specs:
            return self.name
        return f"{self.name}{self.pretty_specs}"

    @property
    def uri(self) -> Optional[str]:
        if self._vcs and self._vcs in self._uri[:4]:
            # handle 'git+https' schemas
            return self._uri[4:]
        return self._uri

    @property
    def vcs(self) -> Optional[str]:
        return self._vcs

    @property
    def revision(self) -> Optional[str]:
        return self._revision

    @property
    def line(self) -> Optional[str]:
        return self._line

    @property
    def specs(self) -> List[Tuple[str, str]]:
        return self._specs

    @property
    def pretty_specs(self) -> str:
        if self.line and self.vcs:
            return self.line
        if self._path:
            return f"-e {self._path}"
        if not self.specs:
            return "*"
        _specs = ["".join(i for i in s) for s in self.specs]
        return "".join(_specs)

    @classmethod
    def from_text(cls, name: str, specs: str) -> 'Package':
        """Create package from text.

        Args:
            name: name of package
            specs: package constraints

        Returns:
            Package instance

        """
        if 'http' in specs:
            req = next(requirements.parse(specs))
            return cls(**req.__dict__)
        if '-e' in specs:
            req = next(requirements.parse(specs))
            return cls(name, req.specs, path=req.path)
        req_name = name
        if specs != '*':
            req_name = f"{name}{specs}"
        req = next(requirements.parse(req_name))
        return cls(req.name, req.specs)

    def __str__(self) -> str:
        return self.full_name
