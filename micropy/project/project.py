# -*- coding: utf-8 -*-

"""Hosts functionality relating to generation of user projects."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

import requirements

from micropy import utils
from micropy.exceptions import StubError
from micropy.logger import Log
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
                 stub_manager=None, **kwargs):
        self._loaded = False
        self.path = Path(path).absolute()
        self.data = self.path / '.micropy'
        self.cache = self.data / '.cache'
        self.info_path = self.path / 'micropy.json'
        self.stub_manager = stub_manager

        self.name = name or self.path.name
        self.stubs = stubs

        self.requirements = self.path / 'requirements.txt'
        self.dev_requirements = self.path / 'dev-requirements.txt'
        self.packages = {}
        self.dev_packages = {'micropy-cli': '*'}
        self.pkg_data = self.data / self.name

        self.config = {'vscode': False, 'pylint': False}
        self.log = Log.add_logger(self.name, show_title=False)
        template_log = Log.add_logger(
            "Templater", parent=self.log, show_title=False)
        self.provider = None
        if templates:
            for key in self.config:
                if key in templates:
                    self.config[key] = True
            self.provider = TemplateProvider(
                templates, log=template_log, **kwargs)

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

    def _resolve_subresource(self, stubs):
        """Resolves stub resource

        Args:
            stubs (stubs): Stubs Passed to Manager
        """
        try:
            resource = set(
                self.stub_manager.resolve_subresource(stubs, self.data))
        except OSError as e:
            msg = "Failed to Create Stub Links!"
            exc = StubError(message=msg)
            self.log.error(str(e), exception=exc)
            sys.exit(1)
        else:
            return resource

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
            file_name = utils.get_url_filename(url)
            _file_name = "".join(self.log.iter_formatted(f"$B[{file_name}]"))
            content = utils.stream_download(
                url, desc=f"{self.log.get_service()} {_file_name}")
            pkg_path = utils.extract_tarbytes(content, tmp_path)
            ignore = ['setup.py', '__version__', 'test_']
            pkg_init = next(pkg_path.rglob("__init__.py"), None)
            py_files = [f for f in pkg_path.rglob(
                "*.py") if not any(i in f.name for i in ignore)]
            stubs = [utils.generate_stub(f) for f in py_files]
            if pkg_init:
                data_path = self.pkg_data / pkg_init.parent.name
                shutil.copytree(pkg_init.parent, data_path)
                return data_path
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
        if pkgs and not self._loaded:
            self.log.title("Fetching Requirements")
        for name, spec in pkgs:
            meta = utils.get_package_meta(name, spec=spec)
            tar_url = meta['url']
            self._fetch_package(tar_url)
        self.update_all()
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
        self.config = data.get("config", self.config)
        templates = [k for k, v in self.config.items() if v]
        self.provider = TemplateProvider(templates, **kwargs)
        self.packages = data.get("packages", self.packages)
        self.dev_packages = data.get("dev-packages", self.dev_packages)
        self.stubs = kwargs.get('stubs', self.stubs)
        self.stub_manager = kwargs.get("stub_manager", self.stub_manager)
        self.stub_manager.verbose_log(verbose)
        self.data.mkdir(exist_ok=True)
        stubs = list(self._load_stubs(_stubs))
        if self.stubs:
            stubs.extend(self.stubs)
        self.stubs = self._resolve_subresource(stubs)
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

    def add_package(self, package, dev=False):
        """Add requirement to project

        Args:
            package (str): package name/spec
            dev (bool, optional): Flag requirement as dev. Defaults to False.

        Returns:
            dict: Dictionary of packages
        """
        pkg = next(requirements.parse(package))
        self.log.info(f"Adding $[{pkg.name}] to requirements...")
        packages = self.dev_packages if dev else self.packages
        if packages.get(pkg.name, None):
            self.log.error(f"$[{package}] is already installed!")
            return None
        specs = "".join(next(iter(pkg.specs))) if pkg.specs else "*"
        packages[pkg.name] = specs
        self.to_json()
        self.load_packages()
        self.log.success("Package installed!")
        return packages

    def _add_pkgs_from_file(self, path, **kwargs):
        """Add packages listed in a file

        Args:
            path (str): path to file

        Returns:
            list of added reqs
        """
        if not path.exists():
            return []
        reqs = list(utils.iter_requirements(path))
        for req in reqs:
            self.add_package(req.line, **kwargs)
        return reqs

    def add_from_requirements(self):
        """Add all packages in requirements.txt files

        Returns:
            List of all added requirements
        """
        reqs = self._add_pkgs_from_file(self.requirements)
        dev_reqs = self._add_pkgs_from_file(self.dev_requirements, dev=True)
        all_reqs = [*reqs, *dev_reqs]
        return all_reqs if all_reqs else None

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
            if self.pkg_data.exists():
                paths.append(self.pkg_data)
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
            "config": self.config,
            "packages": self.packages,
            "dev-packages": self.dev_packages
        }

    def _dump_requirements(self, packages, path):
        """Dumps packages to file at path

        Args:
            packages (dict): dict of packages to dump
            path (str): path to fiel
        """
        if not path.exists():
            path.touch()
        pkgs = [(f"{name}{spec}" if spec and spec != "*" else name)
                for name, spec in packages.items()]
        with path.open('r+') as f:
            content = [c.strip() for c in f.readlines() if c.strip() != '']
            _lines = sorted(set(pkgs) | set(content))
            lines = [l + "\n" for l in _lines]
            f.seek(0)
            f.writelines(lines)

    def to_requirements(self):
        """Dumps requirements to .txt files"""
        self._dump_requirements(self.packages, self.requirements)
        self._dump_requirements(self.dev_packages, self.dev_requirements)

    def to_json(self):
        """Dumps project to data file"""
        with self.info_path.open('w+') as f:
            data = json.dumps(self.info, indent=4)
            f.write(data)

    def render_all(self):
        """Renders all project files"""
        self.log.info("Populating Stub info...")
        for t in self.provider.templates:
            self.provider.render_to(t, self.path, **self.context)
        self.log.success("Stubs Injected!")
        return self.context

    def update_all(self):
        """Updates all project files"""
        self.to_requirements()
        for t in self.provider.templates:
            self.provider.update(t, self.path, **self.context)
        return self.context

    def create(self):
        """creates a new project"""
        self.log.title(f"Initiating $[{self.name}]")
        self.data.mkdir(exist_ok=True, parents=True)
        self.stubs = self._resolve_subresource(self.stubs)
        self.log.info(
            f"Stubs: $[{' '.join(str(s) for s in self.stubs)}]")
        self.log.debug(f"Generated Project Context: {self.context}")
        if self.provider:
            self.log.title("Rendering Templates")
            self.render_all()
        self.update_all()
        self.to_json()
        self.log.success(f"Project Created!")
        return self.path.relative_to(Path.cwd())
