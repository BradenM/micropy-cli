# -*- coding: utf-8 -*-

"""Hosts functionality relating to generation of user projects."""

import json
import shutil
import tempfile
from pathlib import Path

from micropy import utils
from micropy.logger import Log
from micropy.main import MicroPy
from micropy.project.template import TemplateProvider


class Project:
    """Handles Micropy Projects

    Args:
        path (str): Path to project
        name (str, optional): Name of project.
            Defaults to None. If none, path name is used.
        stubs (Stub, optional): List of Stubs to use.
            Defaults to None.
        stub_manager (StubManager, optional): StubManager to source stubs.
                Defaults to None.
    """

    TEMPLATES = TemplateProvider.TEMPLATES

    def __init__(self, path, name=None, templates=[], stubs=None,
                 stub_manager=None):
        self._loaded = False
        self.path = Path(path).absolute()
        self.data = self.path / '.micropy'
        self.cache = self.data / '.cache'
        self.info_path = self.path / 'micropy.json'
        self.stub_manager = stub_manager

        self.name = name or self.path.name
        self.stubs = stubs

        self.packages = {}
        self.dev_packages = {}
        self.pkg_data = self.data / self.name

        self.log = Log.add_logger(self.name, show_title=False)
        template_log = Log.add_logger("Templater", parent=self.log)
        self.provider = None
        if templates:
            self.provider = TemplateProvider(templates, log=template_log)

    def _set_cache(self, key, value):
        """Set key in Project cache

        Args:
            key (str): Key to set
            value (obj): Value to set
        """
        if not self.cache.exists():
            self.cache.write_text("{}")
        data = json.loads(self.cache.read_text())
        data[key] = value
        with self.cache.open('w+') as f:
            json.dump(data, f)

    def _get_cache(self, key):
        """Retrieve value from Project Cache

        Args:
            key (str): Key to retrieve

        Returns:
            obj: Value at key
        """
        if not self.cache.exists():
            return None
        data = json.loads(self.cache.read_text())
        value = data.pop(key, None)
        return value

    def _load_stubs(self, stubs):
        """Loads stubs from info file

        Args:
            stub_list (dict): Dict of Stubs
        """
        for name, location in stubs.items():
            _path = self.path / location
            if Path(_path).exists():
                yield self.stub_manager.add(_path)
            else:
                yield self.stub_manager.add(name)

    def _fetch_package(self, url):
        """Fetch and stub package at url

        Args:
            url (str): URL to fetch

        Returns:
            Path: path to package
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            content = utils.stream_download(url)
            pkg_path = utils.extract_tarbytes(content, tmp_path)
            ignore = ['setup.py', '__', 'test_']
            py_files = [f for f in pkg_path.rglob(
                "*.py") if not any(i in f.name for i in ignore)]
            stubs = [utils.generate_stub(f) for f in py_files]
            for file, stub in stubs:
                shutil.copy2(file, (self.pkg_data / file.name))
                shutil.copy2(stub, (self.pkg_data / stub.name))

    def load_packages(self):
        """Retrieves and stubs project requirements"""
        pkg_keys = set(self.packages.keys())
        pkg_cache = self._get_cache('pkg_loaded')
        new_pkgs = pkg_keys.copy()
        if pkg_cache:
            new_pkgs = new_pkgs - set(pkg_cache)
        pkgs = [(name, s)
                for name, s in self.packages.items() if name in new_pkgs]
        for name, spec in pkgs:
            meta = utils.get_package_meta(name, spec=spec)
            tar_url = meta['url']
            self._fetch_package(tar_url)
        self._set_cache('pkg_loaded', list(pkg_keys))

    def load(self, verbose=True, **kwargs):
        """Load existing project

        Args:
            verbose (bool): Log to stdout. Defaults to True.

        Returns:
            stubs: Project Stubs
        """
        data = json.loads(self.info_path.read_text())
        _stubs = data.get("stubs")
        self.name = data.get("name", self.name)
        self.packages = data.get("packages", self.packages)
        self.dev_packages = data.get("dev-packages", self.packages)
        self.stubs = kwargs.get('stubs', self.stubs)
        self.stub_manager = kwargs.get("stub_manager", self.stub_manager)
        self.stub_manager.verbose_log(verbose)
        self.data.mkdir(exist_ok=True)
        stubs = list(self._load_stubs(_stubs))
        if self.stubs:
            stubs.extend(self.stubs)
        self.stubs = set(
            self.stub_manager.resolve_subresource(stubs, self.data))
        self.pkg_data.mkdir(exist_ok=True)
        self.load_packages()
        self._loaded = True
        if verbose:
            self.log.success(f"\nProject Ready!")
        return self.stubs

    def add_stub(self, stub, **kwargs):
        """Add stub to project

        Args:
            stub (Stub): Stub object to add

        Returns:
            [Stubs]: Project Stubs
        """
        loaded = self.stubs or []
        stubs = [*loaded, stub]
        self.log.info("Loading project...")
        self.load(stubs=stubs, verbose=False, **kwargs)
        self.log.info("Updating Project Info...")
        self.to_json()
        self.log.info(
            f"Project Stubs: $[{' '.join(str(s) for s in self.stubs)}]")
        self.log.success("\nProject Updated!")
        return self.stubs

    def exists(self):
        """Whether this project exists

        Returns:
            bool: True if it exists
        """
        return self.info_path.exists()

    @property
    def context(self):
        """Get project template context"""
        paths = []
        if self.stubs:
            frozen = [s.frozen for s in self.stubs]
            fware_mods = [s.firmware.frozen
                          for s in self.stubs if s.firmware is not None]
            stub_paths = [s.stubs for s in self.stubs]
            paths = [*fware_mods, *frozen, *stub_paths]
        return {
            "stubs": self.stubs,
            "paths": paths,
            "datadir": self.data,
        }

    @property
    def info(self):
        """Project Information"""
        stubs = {s.name: s.stub_version for s in self.stubs}
        return {
            "name": self.name,
            "stubs": stubs,
            "packages": self.packages,
            "dev-packages": self.dev_packages
        }

    def to_json(self):
        """Dumps project to data file"""
        with self.info_path.open('w+') as f:
            data = json.dumps(self.info)
            f.write(data)

    def render_all(self):
        """Renders all project files"""
        self.log.info("Populating Stub info...")
        for t in self.provider.templates:
            self.provider.render_to(t, self.path, **self.context)
            _name = t.capitalize()
            self.log.info(f"$[{_name}] template generated!")
        self.log.success("Stubs Injected!")
        return self.context

    def create(self):
        """creates a new project"""
        self.log.title(f"Initiating $[{self.name}]")
        self.data.mkdir(exist_ok=True, parents=True)
        self.stubs = list(
            self.stub_manager.resolve_subresource(self.stubs, self.data))
        self.log.info(
            f"Stubs: $[{' '.join(str(s) for s in self.stubs)}]")
        self.log.debug(f"Generated Project Context: {self.context}")
        if self.provider:
            self.log.title("Rendering Templates")
            self.render_all()
        self.to_json()
        self.log.success(f"Project Created!")
        return self.path.relative_to(Path.cwd())

    @classmethod
    def resolve(cls, path, verbose=True):
        """Returns project from path if it exists

        Args:
            path (str): Path to test
            verbose (bool): Log to stdout. Defaults to True.

        Returns:
            (Project|None): Project if it exists
        """
        path = Path(path).resolve()
        proj = cls(path)
        if proj.exists():
            micropy = MicroPy()
            if verbose:
                micropy.log.title(f"Loading Project")
            proj.load(stub_manager=micropy.STUBS, verbose=verbose)
            return proj
