# -*- coding: utf-8 -*-

import json
from pathlib import Path
from shutil import copytree

from micropy import data, utils
from micropy.exceptions import StubError, StubValidationError
from micropy.logger import Log
from micropy.stubs import source


class StubManager:
    """Manages a collection of Stubs

    Kwargs:
        resource (str): Default resource path
        repos ([StubRepo]): Repos for Remote Stubs

    Raises:
        StubError: a stub is missing a def file
        StubValidationError: a stubs def file is not valid

    Returns:
        object: Instance of StubManager
    """
    _schema = data.SCHEMAS / 'stubs.json'
    _firm_schema = data.SCHEMAS / 'firmware.json'

    def __init__(self, resource=None, repos=None):
        self._loaded = set()
        self._firmware = set()
        self.resource = resource
        self.repos = repos
        self.log = Log.add_logger('Stubs', stdout=False, show_title=False)
        if self.resource:
            self.load_from(resource, strict=False, skip_firmware=True)
            for stub in self._loaded:
                stub.firmware = self.resolve_firmware(stub)

    def __iter__(self):
        return iter(self._loaded)

    def __len__(self):
        return len(self._loaded)

    def verbose_log(self, state):
        """Enable Stub logging to stdout

        Args:
            state (bool): State to set

        Returns:
            bool: state
        """
        self.log.stdout = state
        return state

    def _load(self, stub_source, strict=True, skip_firmware=False, **kwargs):
        """Loads a stub into StubManager

        Args:
            stub_source (StubSource): Stub Source Instance
            strict (bool, optional): Raise Exception if stub fails to resolve.
                Defaults to True.
            skip_firmware (bool, optional): Skip firmware resolution.
                Defaults to False

        Raises:
            e: Exception raised by resolving failure

        Returns:
            Stub: Instance of Stub
        """
        with stub_source.ready() as src_path:
            try:
                stub_type = self.resolve_stub(src_path)
            except Exception as e:
                self.log.debug(f"{src_path.name} failed to validate: {e}")
                if strict:
                    raise e
            else:
                if stub_type is FirmwareStub:
                    fware = stub_type(src_path, **kwargs)
                    self._firmware.add(fware)
                    self.log.debug(f"Firmware Loaded: {fware}")
                    return fware
                stub = stub_type(src_path, **kwargs)
                if not skip_firmware:
                    fware = self.resolve_firmware(stub)
                    stub.firmware = fware
                self._loaded.add(stub)
                self.log.debug(f"Loaded: {stub}")
                return stub

    def resolve_firmware(self, stub):
        """Resolves FirmwareStub for DeviceStub instance

        Args:
            stub (DeviceStub): Stub to resolve

        Returns:
            FirmwareStub: Instance of FirmwareStub
            NoneType: None if an appropriate
                FirmwareStub cannot be found
        """
        fware_name = stub.firmware_name
        self.log.info(f"Detected Firmware: $[{fware_name}]")
        results = (f for f in self._firmware if f.firmware == fware_name)
        fware = next(results, None)
        if not fware:
            try:
                self.log.info(
                    "Firmware not found locally, attempting to install it...")
                fware = self.add(fware_name)
            except Exception:
                self.log.error("Failed to resolve firmware!")
                return None
            else:
                self.log.success(
                    f"{fware_name} firmware added!", nl=True)
                return fware
        self.log.info(f"$[{fware_name}] is installed already.")
        return fware

    def validate(self, path, schema=None):
        """Validates given stub path against its schema

        Args:
            path (str): path to validate
            schema (str, optional): Path to schema. Defaults to None.
                If None, the DeviceStub schema is used.

        Raises:
            StubError: Raised if no info file can be found
            StubValidationError: Raised if the info file fails validation
        """
        self.log.debug(f"Validating: {path}")
        schema = schema or self._schema
        path = Path(path).resolve()
        stub_info = path / 'info.json'
        val = utils.Validator(schema)
        try:
            val.validate(stub_info)
        except FileNotFoundError:
            raise StubError(f"{path.name} contains no info file!")
        except Exception as e:
            raise StubValidationError(path, str(e))

    def resolve_stub(self, path):
        """Resolves appropriate stub type

        Args:
            path (str): path to stub

        Returns:
            cls: Appropriate class for stub
        """
        try:
            self.validate(path)
        except StubValidationError:
            try:
                self.validate(path, schema=self._firm_schema)
            except Exception as e:
                raise e
            else:
                return FirmwareStub
        except Exception as e:
            raise e
        else:
            return DeviceStub

    def is_valid(self, path):
        """Check if stub is valid without raising an exception

        Args:
            path (str): path to stub

        Returns:
            bool: True if stub is valid
        """
        try:
            self.resolve_stub(path)
        except Exception:
            return False
        else:
            return True

    def load_from(self, directory, *args, **kwargs):
        """Recursively loads stubs from a directory

        Args:
            directory (str): Path to load from

        Returns:
            [DeviceStub]: List of loaded Stubs
        """
        dir_path = Path(str(directory)).resolve()
        dirs = dir_path.iterdir()
        stubs = [self._load(source.get_source(d), *args, **kwargs)
                 for d in dirs]
        return stubs

    def _should_recurse(self, location):
        """Checks for multiple stubs in a location

        Args:
            location (str): location of potential stub

        Raises:
            StubError: No info files could be found

        Returns:
            bool: True if multiple stubs are found
        """
        if not Path(location).exists():
            return False
        path = Path(location).resolve()
        info_glob = list(path.rglob("info.json"))
        if len(info_glob) == 0:
            raise StubError(f"{path.name} contains no info file!")
        if len(info_glob) > 1:
            return True
        return False

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
        if self._should_recurse(location):
            return self.load_from(location, strict=False, copy_to=dest)
        self.log.info(f"Resolving source...")
        stub_source = source.get_source(location, log=self.log)
        return self._load(stub_source, copy_to=dest)

    def from_stubber(self, path, dest):
        """Formats stubs generated by createstubs.py

        Creates a stub package from the stubs generated by
        createstubs.py. Also attempts to auto-resolve the stubs
        firmware name.

        Args:
            path (str): path to generated stubs
            dest (str): path to output

        Returns:
            str: formatted stubs
        """
        _path = Path(path).resolve()
        dest = Path(dest).resolve()
        mod_file = next(_path.rglob("modules.json"))
        path = mod_file.parent
        mod_data = json.load(mod_file.open())
        dev_fware = mod_data['firmware']
        fname = dev_fware.get('name', None)
        out_name = f"{dev_fware['sysname']}"
        # TODO: Attempt to Autoresolve Firmware name and add it to info.json
        if fname:
            out_name = f"{out_name}-{fname}"
        out_name = f"{out_name}-{dev_fware['version']}"
        out_stub = dest / out_name
        info_file = out_stub / 'info.json'
        stub_path = out_stub / 'stubs'
        out_stub.mkdir(exist_ok=True, parents=True)
        json.dump(mod_data, info_file.open('w+'))
        copytree(path, stub_path)
        return out_stub

    def search_remote(self, query):
        """Search all repositories for query

        Args:
            query (str): query to search for

        Returns:
            [tuple]: List of result tuples. The first item
                is the package name, and the second is a bool
                based on whether the package is installed or not
        """
        results = []
        installed = [str(s) for s in self._loaded.union(self._firmware)]
        for repo in self.repos:
            for p in repo.search(query):
                results.append((p, p in installed))
        return sorted(results)


class Stub:
    """Abstract Parent for Stub Related Classes

    Not Meant to be instantiated directly. Contains common logic
    between different types of Stubs (ex. Firmware vs Device)

    Raises:
        NotImplementedError: name property is not implemented

    Returns:
        Instance of Stub
    """

    def __init__(self, path, copy_to=None, **kwargs):
        self.path = Path(path).resolve()
        ref = self.path / 'info.json'
        self.info = json.load(ref.open())
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
    def name(self):
        """Human friendly stub name"""
        raise NotImplementedError

    def __eq__(self, other):
        return self.name == getattr(other, 'name', None)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class DeviceStub(Stub):
    """Handles Device Specific Stubs

    Args:
        path (str): path to stub
        copy_to (str, optional): Path to copy Stub to. Defaults to None.

    Returns:
        Device Stub Instance
    """

    def __init__(self, path, copy_to=None, **kwargs):
        super().__init__(path, copy_to, **kwargs)

        self.stubs = self.path / 'stubs'
        self.frozen = self.path / 'frozen'

        self.firm_info = self.info.get("firmware")
        self.firmware = None
        self.sysname = self.firm_info.get('sysname')
        self.version = self.firm_info.get('version')

    @property
    def firmware_name(self):
        """Return an appropriate firmware name

        Returns:
            str: Name of Firmware
        """
        if isinstance(self.firmware, FirmwareStub):
            return self.firmware.firmware
        fware = self.firm_info.get('name', None)
        if not fware:
            fware = self.firm_info.get('firmware')
        return fware

    @property
    def name(self):
        if not isinstance(self.firmware, FirmwareStub):
            return f"{self.sysname}-{self.version}"
        return f"{self.sysname}-{self.firmware_name}-{self.version}"

    def __repr__(self):
        return (f"DeviceStub(sysname={self.sysname}, firmware="
                f"{self.firmware_name}, version={self.version}, "
                f"path={self.path})")


class FirmwareStub(Stub):
    """Handles Firmware Specific Modules

    Args:
        path (str): path to stub
        copy_to (str, optional): Path to copy Stub to. Defaults to None.

    Returns:
        FirmwareStub Instance
    """

    def __init__(self, path, copy_to=None, **kwargs):
        super().__init__(path, copy_to=copy_to, **kwargs)

        self.frozen = self.path / 'frozen'
        self.repo = self.info.get('repo')
        self.firmware = self.info.get('firmware')

    @property
    def name(self):
        return self.firmware

    def __repr__(self):
        return f"FirmwareStub(firmware={self.firmware}, repo={self.repo})"
