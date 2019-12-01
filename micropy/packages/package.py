# -*- coding: utf-8 -*-


from typing import List, Tuple

from packaging.utils import canonicalize_name


class Package:

    def __init__(self, name: str, specs: List[Tuple[str, str]]):
        """Generic Python Dependency.

        Args:
            name (str): Name of package
            specs (List[Tuple[str, str]]): Package constraints.

        """
        self._name = name
        self._specs = specs

    @property
    def name(self) -> str:
        return canonicalize_name(self._name)

    @property
    def specs(self) -> List[Tuple[str, str]]:
        return self._specs

    @property
    def pretty_specs(self) -> str:
        if not self.specs:
            return "*"
        _specs = ["".join(i for i in s) for s in self.specs]
        return "".join(_specs)

    def __str__(self) -> str:
        return self.name
