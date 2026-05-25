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
    requirement: str, name: Optional[str] = None, **kwargs: Any
) -> Union[LocalDependencySource, PackageDependencySource, VCSDependencySource]:
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
        # requirements-parser >=0.10 splits "-e a/b/c" into path="a/b" and name="c";
        # reassemble so downstream paths still point at the package directory.
        full_path = f"{req.path}/{req.name}" if req.name else req.path
        path = Path(full_path)
        name = name or path.name
        pkg = Package(name, req.specs, path=full_path)
        source = LocalDependencySource(pkg, path)
        return source
    pkg = Package(**req.__dict__)
    if pkg.vcs is not None or pkg.revision is not None:
        return VCSDependencySource(pkg, **kwargs)
    return PackageDependencySource(pkg, **kwargs)


__all__ = [
    "Package",
    "PackageDependencySource",
    "LocalDependencySource",
    "create_dependency_source",
]
