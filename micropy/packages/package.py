# -*- coding: utf-8 -*-


from typing import List, Optional, Tuple

import requirements
from packaging.utils import canonicalize_name
from pathlib import Path


class Package:

    def __init__(self, name: str, specs: List[Tuple[str, str]], path: Optional[str] = None):
        """Generic Python Dependency.

        Args:
            name (str): Name of package
            specs (List[Tuple[str, str]]): Package constraints.
            path: path to package

        """
        self._name = name
        self._specs = specs
        self._path = path
        self.editable = (self._path is not None)

    @property
    def name(self) -> str:
        return canonicalize_name(self._name)

    @property
    def path(self) -> Path:
        return Path(self._path)

    @property
    def full_name(self) -> str:
        if self._path:
            return self.pretty_specs
        if not self._specs:
            return self.name
        return f"{self.name}{self.pretty_specs}"

    @property
    def specs(self) -> List[Tuple[str, str]]:
        return self._specs

    @property
    def pretty_specs(self) -> str:
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
