# -*- coding: utf-8 -*-

import json
from pathlib import Path

from jsonschema import Draft7Validator
from shutil import copytree

from micropy.logger import Log
from micropy.exceptions import StubValidationError


class Stub:
    """Handles Stub Files

    :param str path: path to stub
    :param Optional[str] copy_to: directory to copy stub to if it validates

    """
    SCHEMA = Path(__file__).parent / 'schema.json'

    def __init__(self, path, copy_to=None, **kwargs):
        self.path = path.absolute()
        self.log = Log().add_logger('Stubs', 'yellow')
        try:
            self.validate(self.path)
        except StubValidationError as e:
            raise e
        else:
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

    def validate_json(self, json):
        """Checks json against a schema"""
        schema = json.load(self.SCHEMA.open())
        val = Draft7Validator(schema)
        errors = sorted(val.iter_errors(json))
        if len(errors) <= 0:
            return True
        errors = sorted(val.iter_errors(json), key=str)
        exc = StubValidationError(self, errors)
        self.log.error(exc.message)
        raise exc

    def validate(self, path):
        """Validates stubs"""
        self.log.debug(f"Validating: {path}")
        stub_info = path / 'modules.json'
        if not stub_info.exists():
            raise StubValidationError(
                self, [f"{path.name} contains no modules.json file!"])
        stub_info = json.load(stub_info.open())
        return self.validate_json

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
