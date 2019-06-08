# -*- coding: utf-8 -*-

from shutil import copytree
import re
import json
from jsonschema import validate, Draft7Validator, ValidationError
from pathlib import Path
from micropy import LOG

class Stub:
    """Handles Stub Files

    :param str path: path to stub

    """
    SCHEMA = Path(__file__).parent / 'schema.json'

    def __init__(self, path, *args, **kwargs):
        self.path = path.absolute()
        self.log = LOG.add_logger('Stubs', 'yellow')
        if Stub.validate(self.path):
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

    @staticmethod
    def validate_json(schema, json):
        """Checks json against a schema"""
        try:
            val = Draft7Validator(schema)
            errors = sorted(val.iter_errors(json))
            if len(errors) <= 0:
                return True
            for err in sorted(val.iter_errors(json), key=str):
                print(err.message)
        except ValidationError as e:
            print(e.message)
        return False

    @staticmethod
    def validate(path):
        """Validates stubs"""
        stub_info = path / 'modules.json'
        if not stub_info.exists():
            raise Exception(f"{path.absolute()} contains no modules.json file!")
        schema = json.load(Stub.SCHEMA.open())
        stub_info = json.load(stub_info.open())
        is_valid = Stub.validate_json(schema, stub_info)
        if not is_valid:
            raise Exception("Modules.json contains errors!")
        return is_valid

    def __repr__(self):
        return f"Stub(machine={self.machine}, nodename={self.nodename}, release={self.release}, sysname={self.sysname}, version={self.version}, modules={self.modules})"

    def __str__(self):
        return f"{self.sysname}@{self.version}"
