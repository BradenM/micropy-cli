# -*- coding: utf-8 -*-

import json
from pathlib import Path

from shutil import copytree

from micropy.logger import Log
from micropy.utils import Validator
from micropy.exceptions import StubValidationError


class Stub:
    """Handles Stub Files

    :param str path: path to stub
    :param Optional[str] copy_to: directory to copy stub to if it validates

    """
    SCHEMA = Path(__file__).parent / 'schema.json'

    def __init__(self, path, copy_to=None, **kwargs):
        self.path = path.absolute()
        self.log = Log.add_logger('Stubs', 'yellow')
        self.validate(path)
        module = self.path / 'modules.json'
        info = json.load(module.open())
        device = info.pop(0)
        self.modules = info
        if info[0].get('stubber', None) is None:
            self.modules = info[1:]
        self.machine = device.get('machine')
        self.nodename = device.get('nodename')
        self.release = device.get('release')
        self.sysname = device.get('sysname')
        self.version = device.get('version')
        if copy_to is not None:
            self.copy_to(copy_to)

    def validate(self, path):
        """Validates stubs"""
        self.log.debug(f"Validating: {path}")
        stub_info = path / 'modules.json'
        val = Validator(self.SCHEMA)
        try:
            val.validate(stub_info)
        except FileNotFoundError:
            raise StubValidationError(
                self, [f"{path.name} contains no modules.json file!"])
        except Exception as e:
            raise StubValidationError(self, str(e))

    def copy_to(self, dest):
        """Copy stub to a directory"""
        copytree(self.path, dest)
        self.path = dest
        return self

    def __repr__(self):
        return f"Stub(machine={self.machine}, nodename={self.nodename}, \
                release={self.release}, sysname={self.sysname}, \
                version={self.version}, modules={self.modules})"

    def __str__(self):
        return f"{self.sysname}@{self.version}"
