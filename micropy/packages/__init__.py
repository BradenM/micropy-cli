# -*- coding: utf-8 -*-

"""Packages Module.

Allows user to address different dependency types (package, module,
path, pypi, etc.) through a single uniform api.

"""

from pathlib import Path
from typing import Any, Optional, Union

import requirements

from .package import Package
from .source_package import PackageDependencySource, VCSDependencySource
from .source_path import LocalDependencySource


def create_dependency_source(
        requirement: str,
        name: Optional[str] = None,
        **kwargs: Any) -> Union[LocalDependencySource, PackageDependencySource, VCSDependencySource]:
    """Factory for creating a dependency source object.

    Args:
        requirement (str): Package name/path/constraints in string form.
        name (str, optional): Override package name.
            Defaults to None.

    Returns:
        Appropriate Dependency Source

    """
    req = next(requirements.parse(str(requirement)))
    if req.local_file:
        path = Path(req.path)
        name = name or path.name
        pkg = Package(name, req.specs, path=req.path)
        source = LocalDependencySource(pkg, path)
        return source
    pkg = Package(**req.__dict__)
    if pkg.vcs is not None or pkg.revision is not None:
        return VCSDependencySource(pkg, **kwargs)
    return PackageDependencySource(pkg, **kwargs)


__all__ = ["Package", "PackageDependencySource",
           "LocalDependencySource", "create_dependency_source"]
