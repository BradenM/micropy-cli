"""Main Module."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List, Literal, Optional, Union

from micropy import data, utils
from micropy.exceptions import PyDeviceError
from micropy.logger import Log
from micropy.project import Project, modules
from micropy.pyd import DevicePath, MessageHandlers, ProgressStreamConsumer, PyDevice
from micropy.pyd.backend_rshell import RShellPyDeviceBackend
from micropy.pyd.backend_upydevice import UPyDeviceBackend
from micropy.stubs import RepositoryInfo, StubManager, StubRepository
from micropy.utils.stub import prepare_create_stubs
from pydantic import parse_file_as


class MicroPy:
    """Handles App State Management."""

    RUN_CHECKS = True
    repo: StubRepository
    _stubs: Optional[StubManager] = None

    def __init__(self):
        self.log = Log.get_logger("MicroPy")
        self.verbose = True
        self.log.debug("MicroPy Loaded")
        repo_list = parse_file_as(List[RepositoryInfo], data.REPO_SOURCES)
        self.repo = StubRepository()
        for repo_info in repo_list:
            self.repo = self.repo.add_repository(repo_info)
        if not data.STUB_DIR.exists():
            self.setup()

    def setup(self):
        """Creates necessary directories for micropy."""
        self.log.debug("Running first time setup...")
        self.log.debug(f"Creating .micropy directory @ {data.FILES}")
        data.FILES.mkdir(exist_ok=True)
        data.STUB_DIR.mkdir()

    @property
    def stubs(self) -> StubManager:
        """Primary Stub Manager for MicroPy.

        Returns:
            StubManager: StubManager Instance

        """
        if not self._stubs:
            self._stubs = StubManager(resource=data.STUB_DIR, repos=self.repo)
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
