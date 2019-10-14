# -*- coding: utf-8 -*-

"""Project Packages Module"""

import abc
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

from . import ProjectModule


class PackagesModule(ProjectModule):

    def __init__(self, path, name=None, packages=None, *args, **kwargs):
        self._path = Path(path)
        self._loaded = False
        packages = packages or {}
        self.name = name or "packages"
        self.packages = {**packages}

    @property
    def path(self):
        path = self.parent.path / self._path
        return path

    @property
    def config(self):
        return {
            self.name: self.packages
        }

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
                data_path = self.parent.pkg_data / pkg_init.parent.name
                shutil.copytree(pkg_init.parent, data_path)
                return data_path
            for file, stub in stubs:
                shutil.copy2(file, (self.parent.pkg_data / file.name))
                shutil.copy2(stub, (self.parent.pkg_data / stub.name))

    def load(self):
        """Retrieves and stubs project requirements"""
        self.parent.pkg_data.mkdir(exist_ok=True)
        pkg_keys = set(self.packages.keys())
        pkg_cache = self.parent._get_cache('pkg_loaded')
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
        self.update()
        self.parent._set_cache('pkg_loaded', list(pkg_keys))

    def create(self):
        pass

    def update(self):
        """Dumps packages to file at path"""
        if not self.path.exists():
            self.path.touch()
        pkgs = [(f"{name}{spec}" if spec and spec != "*" else name)
                for name, spec in self.packages.items()]
        with self.path.open('r+') as f:
            content = [c.strip() for c in f.readlines() if c.strip() != '']
            _lines = sorted(set(pkgs) | set(content))
            lines = [l + "\n" for l in _lines]
            f.seek(0)
            f.writelines(lines)
