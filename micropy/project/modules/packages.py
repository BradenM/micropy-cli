# -*- coding: utf-8 -*-

"""Project Packages Module."""

import shutil
from pathlib import Path
from typing import Any, Union

from boltons import fileutils

from micropy import utils
from micropy.config import Config
from micropy.packages import (LocalDependencySource, Package,
                              PackageDependencySource,
                              create_dependency_source)
from micropy.project.modules import ProjectModule


class PackagesModule(ProjectModule):
    """Project Module for handling requirements.

    Args:
        path (str): Path to create requirements file at.
        packages (dict, optional): Initial packages to use.
            Defaults to None.

    """
    name: str = "packages"
    PRIORITY: int = 8

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self._path = Path(path)

    @property
    def packages(self):
        _packages = self.config.get(self.name, {})
        return _packages

    @property
    def path(self):
        """Path to requirements file.

        Returns:
            Path: Path to file

        """
        path = self.parent.path / self._path
        return path

    @property
    def pkg_path(self):
        """Path to package data folder.

        Returns:
            Path: Path to folder.

        """
        return self.parent.data_path / self.parent.name

    @property
    def config(self) -> Config:
        """Config values specific to component.

        Returns:
            Component config.

        """
        return self.parent.config

    @property
    def context(self) -> Config:
        """Context values specific to component.

        Returns:
            Context values.

        """
        return self.parent.context

    def install_package(self, source: Union[LocalDependencySource, PackageDependencySource]) -> Any:
        with source as files:
            if source.is_local:
                self.log.debug(f"installing {source} as local")
                return
            if isinstance(files, list):
                self.log.debug(f"installing {source} as module(s)")
                # Iterates over flattened list of stubs tuple
                file_paths = [(f, (self.pkg_path / f.name)) for f in list(sum(files, ()))]
                for paths in file_paths:
                    return shutil.move(*paths)  # overwrites if existing
            self.log.debug(f'installing {source} as package')
            pkg_path = self.pkg_path / source.package.name
            return fileutils.copytree(files, pkg_path)

    @ProjectModule.hook(dev=False)
    def add_from_file(self, path=None, dev=False, **kwargs):
        """Loads all requirements from file.

        Args:
            path (str): Path to file. Defaults to self.path.
            dev (bool, optional): If dev requirements should be loaded.
                Defaults to False.

        """
        reqs = utils.iter_requirements(self.path)
        for req in reqs:
            self.add_package(req)
        return reqs

    @ProjectModule.hook()
    def add_package(self, package, dev=False, **kwargs):
        """Add requirement to project.

        Args:
            package (str): package name/spec
            dev (bool, optional): If dev requirements should be loaded.
                Defaults to False.

        Returns:
            dict: Dictionary of packages

        """
        self.log.debug(f"adding new dependency: {package}")
        source = create_dependency_source(package, **kwargs)
        pkg = source.package
        self.log.info(f"Adding $[{pkg.name}] to requirements...")
        if self.packages.get(pkg.name, None):
            self.log.error(f"$[{pkg}] is already installed!")
            self.update()
            return None
        try:
            self.config.add(self.name + '/' + pkg.name, pkg.pretty_specs)
            self.load()
        except ValueError as e:
            self.log.error(f"Failed to find package $[{pkg.name}]!")
            self.log.error("Is it available on PyPi?", exception=e)
            self.config.pop(self.name + '/' + pkg.name)
        except Exception as e:
            self.log.error(
                f"An error occured during the installation of $[{pkg.name}]!",
                exception=e)
            self.config.pop(self.name + '/' + pkg.name)
        else:
            self.log.success("Package installed!")
        finally:
            return self.packages

    def load(self, fetch=True, **kwargs):
        """Retrieves and stubs project requirements."""
        self.pkg_path.mkdir(exist_ok=True)
        packages = self.config.get(self.name, {})
        if self.path.exists():
            reqs = utils.iter_requirements(self.path)
            for r in reqs:
                pkg = create_dependency_source(r.line).package
                if not packages.get(pkg.name):
                    packages.update({pkg.name: pkg.pretty_specs})
        pkg_keys = set(packages.keys())
        pkg_cache = self.parent._get_cache(self.name)
        new_pkgs = pkg_keys.copy()
        if pkg_cache:
            new_pkgs = new_pkgs - set(pkg_cache)
        new_packages = [Package.from_text(name, spec)
                        for name, spec in packages.items() if name in new_pkgs]
        if fetch:
            if new_packages:
                self.log.title("Fetching Requirements")
            for req in new_packages:
                def format_desc(p): return "".join(self.log.iter_formatted(f"$B[{p}]"))
                source = create_dependency_source(
                    str(req),
                    name=req.name,
                    format_desc=lambda p: f"{self.log.get_service()} {format_desc(p)}")
                self.install_package(source)
        self.update()
        self.parent._set_cache(self.name, list(pkg_keys))

    def create(self):
        """Create project files."""
        self.config.add(self.name, {})
        return self.update()

    def update(self):
        """Dumps packages to file at path."""
        if not self.path.exists():
            self.path.touch()
        pkgs = [Package.from_text(name, spec) for name, spec in self.packages.items()]
        self.log.debug(f'dumping to {self.path.name}')
        with self.path.open('r+') as f:
            content = [c.strip() for c in f.readlines() if c.strip() != '']
            _lines = sorted(set(str(p) for p in pkgs) | set(content))
            lines = [l + "\n" for l in _lines]
            self.log.debug(f"dumping: {lines}")
            f.seek(0)
            f.writelines(lines)
        local_paths = [p.path for p in pkgs if p.editable]
        self.context.add('local_paths', local_paths)
        self.context.extend('paths', [self.pkg_path], unique=True)


class DevPackagesModule(PackagesModule):
    """Project Module for Dev Packages."""
    PRIORITY: int = 7

    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)
        self.name = "dev-packages"

    def create(self):
        """Creates component."""
        super().create()
        self.config.add(f"{self.name}/micropy-cli", '*')

    def load(self, *args, **kwargs):
        """Load component."""
        super().load(*args, **kwargs, fetch=False)

    @ProjectModule.hook(dev=True)
    def add_package(self, package, **kwargs):
        """Adds package."""
        return super().add_package(package, **kwargs)

    @ProjectModule.hook(dev=True)
    def add_from_file(self, path=None, **kwargs):
        """Adds packages from file."""
        return super().add_from_file(path=path, **kwargs)
