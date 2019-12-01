# -*- coding: utf-8 -*-

"""Packages Module."""

from pathlib import Path
from typing import Any, Union, Optional

import requirements

from .package import Package
from .source_package import PackageDependencySource
from .source_path import LocalDependencySource


def create_dependency_source(
        requirement: str,
        name: Optional[str] = None,
        **kwargs: Any) -> Union[LocalDependencySource, PackageDependencySource]:
    req = next(requirements.parse(str(requirement)))
    if req.local_file:
        path = Path(req.path)
        name = name or path.name
        pkg = Package(name, req.specs)
        source = LocalDependencySource(pkg, path)
        return source
    pkg = Package(req.name, req.specs)
    return PackageDependencySource(pkg, **kwargs)


__all__ = ["Package", "PackageDependencySource",
           "LocalDependencySource", "create_dependency_source"]
