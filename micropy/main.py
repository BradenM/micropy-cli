# -*- coding: utf-8 -*-

"""Main Module"""

import tempfile
from pathlib import Path

from micropy.logger import Log
from micropy.stubs import StubManager
from micropy.utils import PyboardWrapper


class MicroPy:
    """Parent class for handling setup and variables"""
    LIB = Path(__file__).parent / 'lib'
    STUBBER = LIB / 'stubber'
    FILES = Path.home() / '.micropy'
    STUB_DIR = FILES / 'stubs'
    STUBS = None

    def __init__(self):
        self.log = Log.get_logger('MicroPy')
        self.setup()

    def setup(self):
        """creates necessary directories for micropy"""
        self.log.debug("\n---- MicropyCLI Session ----")
        self.log.debug("Loading stubs...")
        if self.STUB_DIR.exists():
            self.STUBS = StubManager(resource=self.STUB_DIR)
            return self.STUBS
        self.log.debug("Running first time setup...")
        self.log.debug(f"Creating .micropy directory @ {self.FILES}")
        self.FILES.mkdir(exist_ok=True)
        self.STUB_DIR.mkdir()
        initial_stubs_dir = self.STUBBER / 'stubs'
        self.log.debug("Adding stubs from Josverl/micropython-stubber")
        with self.log.silent():
            self.STUBS = StubManager(resource=self.STUB_DIR)
            self.STUBS.add(initial_stubs_dir)
            return self.STUBS

    def create_stubs(self, port):
        """Create and add stubs from Pyboard

        Args:
            port (str): Port of Pyboard

        Returns:
            Stub: generated stub
        """
        # TODO: Probably move this functionality to cli module
        self.log.info(f"Connecting to Pyboard @ $[{port}]...")
        try:
            pyb = PyboardWrapper(port)
        except SystemExit:
            self.log.error(
                f"Failed to connect, are you sure $[{port}] is correct?")
            return None
        self.log.success("Connected!")
        # TODO: determine which script to use based on device
        script_path = self.STUBBER / 'minified.py'
        self.log.info("Executing stubber on pyboard...")
        try:
            pyb.run(script_path)
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
            stub = self.STUBS.add(stub_path)
        self.log.success(f"Added {stub.name} to stubs!")
        return stub
