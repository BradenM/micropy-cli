# -*- coding: utf-8 -*-

import json
from pathlib import Path
from shutil import copytree

from micropy import data, utils
from micropy.exceptions import StubValidationError
from micropy.logger import Log
from micropy.stubs import source


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
    _schema = data.SCHEMAS / 'stubs.json'

    def __init__(self, resource=None, repos=None):
        self._loaded = set()
        self.resource = resource
        self.repos = repos
        self.log = Log.add_logger('Stubs', 'yellow')
        if self.resource:
            self.load_from(resource)

    def __iter__(self):
        return iter(self._loaded)

    def __len__(self):
        return len(self._loaded)

    def _load(self, stub_source, *args, **kwargs):
        """Loads a stub"""
        with stub_source.ready() as src_path:
            try:
                self.validate(src_path)
            except StubValidationError as e:
                self.log.debug(f"{src_path.name} failed to validate: {e}")
            else:
                stub = Stub(src_path, *args, **kwargs)
                self._loaded.add(stub)
                self.log.debug(f"Loaded: {stub}")
                return stub

    def validate(self, path):
        """Validates stubs"""
        self.log.debug(f"Validating: {path}")
        path = Path(path).resolve()
        stub_info = path / 'info.json'
        val = utils.Validator(self._schema)
        try:
            val.validate(stub_info)
        except FileNotFoundError:
            raise StubValidationError(
                path, [f"{path.name} contains no info file!"])
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
        stubs = [self._load(source.get_source(d), *args, **kwargs)
                 for d in dirs]
        return stubs

    def add(self, location, dest=None):
        """Add stub(s) from source

        Args:
            source (str): path to stub(s)
            dest (str, optional): path to copy stubs to.
                Defaults to self.resource

        Raises:
            TypeError: No resource or destination provided
        """
        _dest = dest or self.resource
        if not _dest:
            raise TypeError("No Stub Destination Provided!")
        dest = Path(str(_dest)).resolve()
        if utils.is_existing_dir(location) and not self.is_valid(location):
            return self.load_from(location, copy_to=dest)
        stub_source = source.get_source(location)
        return self._load(stub_source, copy_to=dest)


class Stub:
    """Handles Stub Files

    :param str path: path to stub
    :param Optional[str] copy_to: directory to copy stub to if it validates

    """

    def __init__(self, path, copy_to=None, **kwargs):
        self.path = path.absolute()
        self.log = Log.add_logger('Stubs', 'yellow')
        ref = self.path / 'info.json'
        info = json.load(ref.open())

        self.stubs = self.path / 'stubs'
        self.frozen = self.path / 'frozen'

        self.firmware = info.get("firmware")
        self.sysname = self.firmware.get('sysname')
        self.version = self.firmware.get('version')

        self.name = (
            f"{self.sysname}-{self.firmware_name}-{self.version}")
        if copy_to is not None:
            self.copy_to(copy_to)

    def copy_to(self, dest, name=None):
        """Copy stub to a directory"""
        if not name:
            dest = Path(dest) / self.path.name
        copytree(self.path, dest)
        self.path = dest
        return self

    @property
    def firmware_name(self):
        """Return an appropriate firmware name

        Returns:
            str: Name of Firmware
        """
        fware = self.firmware.get('name', None)
        if not fware:
            fware = self.firmware.get('firmware')
        return fware

    def __eq__(self, other):
        return self.name == getattr(other, 'name', None)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return (f"Stub(sysname={self.sysname}, firmware={self.firmware_name},"
                f" version={self.version}, path={self.path})")

    def __str__(self):
        return self.name
