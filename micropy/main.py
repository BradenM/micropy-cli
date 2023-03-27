"""Main Module."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import attr
from micropy import data, utils
from micropy.logger import Log
from micropy.project import Project, modules
from micropy.stubs import RepositoryInfo, StubManager, StubRepository
from pydantic import parse_file_as


@attr.define(kw_only=True)
class MicroPyOptions:
    root_dir: Path = attr.field(default=data.FILES)
    stubs_dir: Path = attr.Factory(lambda self: self.root_dir / "stubs", takes_self=True)


class MicroPy:
    """Handles App State Management."""

    RUN_CHECKS = True
    repo: StubRepository
    config: MicroPyOptions
    _stubs: Optional[StubManager] = None

    def __init__(self, *, options: Optional[MicroPyOptions] = None):
        self.config = options or MicroPyOptions()
        self.log = Log.get_logger("MicroPy")
        self.verbose = True
        self.log.debug("MicroPy Loaded")
        repo_list = parse_file_as(List[RepositoryInfo], data.REPO_SOURCES)
        self.repo = StubRepository()
        for repo_info in repo_list:
            self.repo = self.repo.add_repository(repo_info)
        if not self.config.stubs_dir.exists():
            self.setup()

    def setup(self):
        """Creates necessary directories for micropy."""
        self.log.debug("Running first time setup...")
        self.log.debug(f"Creating .micropy directory @ {self.config.root_dir}")
        self.config.stubs_dir.mkdir(parents=True, exist_ok=True)

    @property
    def stubs(self) -> StubManager:
        """Primary Stub Manager for MicroPy.

        Returns:
            StubManager: StubManager Instance

        """
        if not self._stubs:
            self._stubs = StubManager(resource=self.config.stubs_dir, repos=self.repo)
        return self._stubs

    @utils.lazy_property
    def project(self):
        """Current active project if available.

        Returns:
            Project: Instance of Current Project

        """
        proj = self.resolve_project(".", verbose=self.verbose)
        return proj

    def resolve_project(self, path, verbose=True):
        """Returns project from path if it exists.

        Args:
            path (str): Path to test
            verbose (bool): Log to stdout. Defaults to True.

        Returns:
            Project if it exists

        """
        path = Path(path).absolute()
        proj = Project(path)
        proj.add(modules.StubsModule, self.stubs)
        proj.add(modules.PackagesModule, "requirements.txt")
        proj.add(modules.DevPackagesModule, "dev-requirements.txt")
        proj.add(modules.TemplatesModule, run_checks=self.RUN_CHECKS)
        if proj.exists:
            if verbose:
                self.log.title("Loading Project")
            proj.load()
            if verbose:
                self.log.success("Ready!")
            return proj
        return proj
