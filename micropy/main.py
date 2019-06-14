# -*- coding: utf-8 -*-

"""Main Module"""

import tempfile
from pathlib import Path

from rshell import main as rsh

from micropy.stubs import Stub
from micropy.logger import Log
from micropy.exceptions import StubValidationError


class MicroPy:
    """Parent class for handling setup and variables"""
    LIB = Path(__file__).parent / 'lib'
    STUBBER = LIB / 'stubber'
    FILES = Path.home() / '.micropy'
    STUB_DIR = FILES / 'stubs'
    STUBS = []

    def __init__(self):
        self.log = Log().get_logger('MicroPy')
        self.setup()

    def setup(self):
        """creates necessary directories for micropy"""
        self.log.debug("\n---- MicropyCLI Session ----")
        self.log.debug("Loading stubs...")
        MicroPy.STUBS = [Stub(i) for i in self.STUB_DIR.iterdir()
                         ] if self.STUB_DIR.exists() else []
        [self.log.debug(f"Loaded: {stub}") for stub in self.STUBS]
        if not self.STUB_DIR.exists():
            self.log.debug("Running first time setup...")
            self.log.debug(f"Creating .micropy directory @ {self.FILES}")
            self.FILES.mkdir(exist_ok=True)
            self.STUB_DIR.mkdir()
            initial_stubs_dir = self.STUBBER / 'stubs'
            self.log.debug("Adding stubs from Josverl/micropython-stubber")
            with self.log.silent():
                for stub in initial_stubs_dir.iterdir():
                    self.add_stub(stub)
            return True
        return False

    def add_stub(self, path):
        """Adds stub to micropy folder

        :param str path: path of stub to add

        """
        stub_path = Path(path)
        self.log.info(f"Adding $[{stub_path.name}] to stubs...")
        stub_out = self.STUB_DIR / stub_path.name
        try:
            stub = Stub(path, copy_to=stub_out)
        except StubValidationError:
            self.log.error(f"{stub_path.name} is not a valid stub!")
        else:
            self.STUBS.append(stub)
            self.log.debug(f"Added New Stub: {stub}")
            self.log.success("Done!")
            return stub

    def create_stubs(self, port):
        """Create stubs from a pyboard

        :param str port: port of pyboard

        """
        create_script = self.STUBBER / 'createstubs.py'
        stubber_logger = self.STUBBER / 'lib' / 'logging.py'
        self.log.info(f"Connecting to PyBoard @ $[{port}]...")
        rsh.ASCII_XFER = False
        rsh.connect(port)
        self.log.success("Connected!")
        dev = rsh.DEVS[0]
        self.log.info("Uploading $[createstubs.py]...")
        rsh.cp(str(create_script.absolute()),
               f"{dev.name_path}/{create_script.name}")
        rsh.cp(str(stubber_logger.absolute()),
               f"{dev.name_path}/{stubber_logger.name}")
        self.log.success("Done!")
        self.log.info("Executing $[createstubs.py]")
        pyb = dev.pyb
        pyb.enter_raw_repl()
        pyb.exec("import createstubs")
        pyb.exit_raw_repl()
        self.log.success("Done!")
        self.log.info("Downloading Stubs...")
        stub_name = rsh.auto(
            rsh.listdir_stat, f'{dev.name_path}/stubs',
            show_hidden=False)[0][0]
        with tempfile.TemporaryDirectory() as tmpdir:
            rsh.rsync(
                f"{dev.name_path}/stubs", tmpdir, recursed=True, mirror=False,
                dry_run=False, print_func=lambda * args: None,
                sync_hidden=False)
            stub_path = Path(tmpdir) / stub_name
            self.add_stub(stub_path)
        self.log.success("Done!")
        return self.list_stubs()

    def list_stubs(self):
        """Lists all available stubs"""
        self.log.info("$w[Available Stubs:]")
        [self.log.info(str(i)) for i in self.STUBS]
        self.log.info(f"$[Total Stubs:] {len(self.STUBS)}")
