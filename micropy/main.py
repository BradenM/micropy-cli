# -*- coding: utf-8 -*-

"""Main Module"""

import sys
import tempfile
from pathlib import Path

from micropy import data, utils
from micropy.lib.stubber import process as stubber
from micropy.logger import Log
from micropy.project import Project
from micropy.stubs import StubManager, source


class MicroPy:
    """Handles App State Management"""
    RUN_CHECKS = True

    def __init__(self):
        self.log = Log.get_logger('MicroPy')
        self.verbose = True
        self.log.debug("\n---- MicropyCLI Session ----")
        if not data.STUB_DIR.exists():
            self.setup()

    def setup(self):
        """creates necessary directories for micropy"""
        self.log.debug("Running first time setup...")
        self.log.debug(f"Creating .micropy directory @ {data.FILES}")
        data.FILES.mkdir(exist_ok=True)
        data.STUB_DIR.mkdir()

    @utils.lazy_property
    def stubs(self):
        repo_list = data.REPO_SOURCES.read_text()
        repos = source.StubRepo.from_json(repo_list)
        return StubManager(resource=data.STUB_DIR, repos=repos)

    @utils.lazy_property
    def project(self):
        proj = self.resolve_project('.', verbose=self.verbose)
        return proj

    def resolve_project(self, path, verbose=True):
        """Returns project from path if it exists

        Args:
            path (str): Path to test
            verbose (bool): Log to stdout. Defaults to True.

        Returns:
            (Project|None): Project if it exists
        """
        path = Path(path).absolute()
        proj = Project(path, run_checks=self.RUN_CHECKS)
        if proj.exists():
            if verbose:
                self.log.title(f"Loading Project")
            proj.load(stub_manager=self.stubs, verbose=verbose,
                      run_checks=self.RUN_CHECKS)
            return proj
        return None

    def create_stubs(self, port, verbose=False):
        """Create and add stubs from Pyboard

        Args:
            port (str): Port of Pyboard

        Returns:
            Stub: generated stub
        """
        self.log.title(f"Connecting to Pyboard @ $[{port}]")
        try:
            pyb = utils.PyboardWrapper(port, verbose=verbose)
        except SystemExit:
            self.log.error(
                f"Failed to connect, are you sure $[{port}] is correct?")
            return None
        self.log.success("Connected!")
        try:
            script = stubber.minify_script()
        except AttributeError:
            self.log.error("\nPyminifier not found!")
            self.log.info(
                ("For device stub creation, micropy-cli depends"
                 " on $B[pyminifer]."))
            self.log.info(
                ("Please install via: $[pip install micropy-cli[create_stubs]]"
                 " and try again."))
            sys.exit(1)
        self.log.info("Executing stubber on pyboard...")
        try:
            pyb.run(script,
                    format_output=lambda x: x.split("to file:")[0].strip())
        except Exception as e:
            # TODO: Handle more usage cases
            self.log.error(f"Failed to execute script: {str(e)}")
            return None
        self.log.success("Done!")
        self.log.info("Copying stubs...")
        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = pyb.copy_dir("/stubs", tmpdir)
            stub_path = next(out_dir.iterdir())
            self.log.info(f"Copied Stubs: $[{stub_path.name}]")
            stub_path = self.stubs.from_stubber(stub_path, out_dir)
            stub = self.stubs.add(stub_path)
        self.log.success(f"Added {stub.name} to stubs!")
        return stub
