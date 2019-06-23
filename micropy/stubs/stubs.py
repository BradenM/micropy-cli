# -*- coding: utf-8 -*-

import json
from pathlib import Path

from shutil import copytree

from micropy.logger import Log
from micropy.utils import Validator
from micropy.exceptions import StubValidationError


class StubManager:
    """Manager for Stub Instances"""
    _schema = Path(__file__).parent / 'schema.json'

    def __init__(self):
        self._loaded = set()
        self.log = Log.add_logger('Stubs', 'yellow')

    def __iter__(self):
        return iter(self._loaded)

    def __len__(self):
        return len(self._loaded)

    def _load(self, path, *args, **kwargs):
        """Loads a stub"""
        try:
            self.validate(path)
        except StubValidationError:
            pass
        else:
            stub = Stub(path, *args, **kwargs)
            self._loaded.add(stub)
            return stub

    def validate(self, path):
        """Validates stubs"""
        self.log.debug(f"Validating: {path}")
        stub_info = path / 'modules.json'
        val = Validator(self._schema)
        try:
            val.validate(stub_info)
        except FileNotFoundError:
            raise StubValidationError(
                path, [f"{path.name} contains no modules.json file!"])
        except Exception as e:
            raise StubValidationError(path, str(e))

    def load_from(self, directory, *args, **kwargs):
        """Load all stubs in a directory"""
        dir_path = Path(str(directory)).resolve()
        dirs = dir_path.iterdir()
        stubs = [self._load(d, *args, **kwargs) for d in dirs]
        return stubs

    def add_from(self, source_dir, dest_dir):
        """Add all stubs in a directory"""
        dest_path = Path(str(dest_dir)).resolve()
        return self.load_from(source_dir, copy_to=dest_dir)

    def add(self, source_dir, dest_dir):
        """add single stub"""
        source_path = Path(str(source_dir)).resolve()
        dest_path = Path(str(dest_dir)).resolve()
        return self._load(source_dir, copy_to=dest_dir)


class Stub:
    """Handles Stub Files

    :param str path: path to stub
    :param Optional[str] copy_to: directory to copy stub to if it validates

    """

    def __init__(self, path, copy_to=None, **kwargs):
        self.path = path.absolute()
        self.log = Log.add_logger('Stubs', 'yellow')
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

    def copy_to(self, dest, name=None):
        """Copy stub to a directory"""
        if not name:
            dest = Path(dest) / self.path.name
        copytree(self.path, dest)
        self.path = dest
        return self

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return f"Stub(machine={self.machine}, nodename={self.nodename}, release={self.release}, sysname={self.sysname}, version={self.version})"

    def __str__(self):
        return f"{self.sysname}@{self.version}"
