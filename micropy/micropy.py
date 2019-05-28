# -*- coding: utf-8 -*-

from pathlib import Path

from micropy.logger import ServiceLog
from micropy.stubs import Stub

class MicroPy:
    """Parent class for handling setup and variables"""
    TEMPLATE = Path(__file__).parent / 'template'
    FILES = Path.home() / '.micropy'
    STUB_DIR = FILES / 'stubs'
    CREATE_STUBS = FILES / 'createstubs.py'
    STUBS = [Stub(i) for i in STUB_DIR.iterdir()]

    def __init__(self):
        setup = self.setup()
        self.log = ServiceLog('MicroPy', 'bright_blue', root=True)
        self.log.debug("\n---- MicropyCLI Session ----")
        if setup:
            self.log.info("Missing .micropy folder, created it.")

    def setup(self):
        """creates necessary directories for micropy"""
        if not self.FILES.exists():
            self.FILES.mkdir()
            return True
        return False

    def add_stub(self, path):
        """Adds stub to micropy folder

        :param str path: path of stub to add

        """
        stub_path = Path(path)
        self.log.info(f"Adding $[{stub_path.name}] to stubs...")
        stub = Stub.create_from_path(self.STUB_DIR, stub_path)
        self.STUBS.append(stub)
        self.log.success("Done!")
        return stub

    def list_stubs(self):
        """Lists all available stubs"""
        self.log.info("$w[Available Stubs:]")
        [self.log.info(i.name) for i in self.STUBS]
        self.log.info(f"$[Total Stubs:] {len(self.STUBS)}")
        