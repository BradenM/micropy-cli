# -*- coding: utf-8 -*-

"""Main Module"""

import sys
import tempfile
from pathlib import Path

from micropy import data, utils
from micropy.lib.stubber import process as stubber
from micropy.logger import Log
from micropy.stubs import StubManager, source


class MicroPy:
    """Parent class for handling setup and variables"""
    LIB = Path(__file__).parent / 'lib'
    STUBBER = LIB / 'stubber'
    FILES = Path.home() / '.micropy'
    STUB_DIR = FILES / 'stubs'
    STUBS = None
    REPOS = data.PATH / 'sources.json'

    def __init__(self):
        self.log = Log.get_logger('MicroPy')
        self.setup()

    def setup(self):
        """creates necessary directories for micropy"""
        self.log.debug("\n---- MicropyCLI Session ----")
        self.log.debug("Loading stubs...")
        if self.STUB_DIR.exists():
            repo_list = self.REPOS.read_text()
            repos = source.StubRepo.from_json(repo_list)
            self.STUBS = StubManager(resource=self.STUB_DIR, repos=repos)
            return self.STUBS
        self.log.debug("Running first time setup...")
        self.log.debug(f"Creating .micropy directory @ {self.FILES}")
        self.FILES.mkdir(exist_ok=True)
        self.STUB_DIR.mkdir()
        return self.setup()

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
            stub_path = self.STUBS.from_stubber(stub_path, out_dir)
            stub = self.STUBS.add(stub_path)
        self.log.success(f"Added {stub.name} to stubs!")
        return stub
