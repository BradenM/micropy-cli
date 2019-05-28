# -*- coding: utf-8 -*-

from pathlib import Path
from micropy.logger import ServiceLog

class MicroPy:
    TEMPLATE = Path(__file__).parent / 'template'
    FILES = Path.home() / '.micropy'
    STUB_DIR = FILES / 'stubs'
    CREATE_STUBS = FILES / 'createstubs.py'

    def __init__(self):
        setup = self.setup()
        self.log = ServiceLog('MicroPy', 'bright_blue', root=True)
        self.log.debug("\n---- MicropyCLI Session ----")
        if setup:
            self.log.info("Missing .micropy folder, created it.")
        
    def setup(self):
        if not self.FILES.exists():
            self.FILES.mkdir()
            return True
        return False
