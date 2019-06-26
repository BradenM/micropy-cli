# -*- coding: utf-8 -*-

import json
from pathlib import Path
from shutil import copytree

from micropy.exceptions import StubValidationError
from micropy.logger import Log
from micropy.utils import Validator


class StubManager:
    """Manages a collection of Stubs

    Kwargs:
        resource (str): Default resource path

    Raises:
        StubValidationError: a stub is missing a def file
        StubValidationError: a stubs def file is not valid

    Returns:
        object: Instance of StubManager
    """
    _schema = Path(__file__).parent / 'schema.json'

    def __init__(self, resource=None):
        self._loaded = set()
        self.resource = resource
        self.log = Log.add_logger('Stubs', 'yellow')
        if self.resource:
            self.load_from(resource)

    def __iter__(self):
        return iter(self._loaded)

    def __len__(self):
        return len(self._loaded)

    def _load(self, path, *args, **kwargs):
        """Loads a stub"""
        try:
            self.validate(path)
        except StubValidationError as e:
            self.log.debug(f"{path.name} failed to validate: {e.message}")
        else:
            stub = Stub(path, *args, **kwargs)
            self._loaded.add(stub)
            self.log.debug(f"Loaded: {stub}")
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

    def is_valid(self, path):
        """Check if stub is valid without raising an exception

        Args:
            path (str): path to stub

        Returns:
            bool: True if stub is valid
        """
        try:
            self.validate(path)
        except StubValidationError:
            return False
        else:
            return True

    def load_from(self, directory, *args, **kwargs):
        """Load all stubs in a directory"""
        dir_path = Path(str(directory)).resolve()
        dirs = dir_path.iterdir()
        stubs = [self._load(d, *args, **kwargs) for d in dirs]
        return stubs

    def add(self, source, dest=None):
        """Add stub(s) from source

        Args:
            source (str): path to stub(s)
            dest (str, optional): path to copy stubs to.
                Defaults to self.resource

        Raises:
            TypeError: No resource or destination provided
        """
        source_path = Path(str(source)).resolve()
        _dest = dest or self.resource
        if not _dest:
            raise TypeError("No Stub Destination Provided!")
        dest = Path(str(_dest)).resolve()
        if not self.is_valid(source_path):
            return self.load_from(source_path, copy_to=dest)
        return self._load(source_path, copy_to=dest)


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
        self.name = f"{self.sysname}@{self.version}"
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
        return self.name == getattr(other, 'name', None)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return (f"Stub(machine={self.machine}, nodename={self.nodename},"
                f" release={self.release}, sysname={self.sysname},"
                f" version={self.version})")

    def __str__(self):
        return self.name
