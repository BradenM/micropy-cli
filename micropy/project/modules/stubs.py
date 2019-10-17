# -*- coding: utf-8 -*-

"""Project Stubs Module"""

import sys
from pathlib import Path

from micropy import utils
from micropy.exceptions import StubError
from micropy.project.modules import ProjectModule


class StubsModule(ProjectModule):

    def __init__(self, stub_manager, stubs=None):
        self.stub_manager = stub_manager
        self._stubs = stubs

    @property
    def context(self):
        """Get project template context"""
        paths = []
        _paths = self.parent._context.get('paths', [])
        if self.stubs:
            frozen = [s.frozen for s in self.stubs]
            fware_mods = [s.firmware.frozen
                          for s in self.stubs if s.firmware is not None]
            stub_paths = [s.stubs for s in self.stubs]
            paths = set([*fware_mods, *frozen, *stub_paths])
        paths = list(paths.union(_paths))
        return {
            "stubs": set(self.stubs),
            "paths": paths,
            "datadir": self.parent.data_path,
        }

    @property
    def config(self):
        stubs = {s.name: s.stub_version for s in self.stubs}
        return {
            'stubs': stubs
        }

    @utils.lazy_property
    def stubs(self):
        return self._resolve_subresource(self._stubs)

    def _resolve_subresource(self, stubs):
        """Resolves stub resource

        Args:
            stubs (stubs): Stubs Passed to Manager
        """
        try:
            resource = set(
                self.stub_manager.resolve_subresource(stubs,
                                                      self.parent.data_path))
        except OSError as e:
            msg = "Failed to Create Stub Links!"
            exc = StubError(message=msg)
            self.log.error(str(e), exception=exc)
            sys.exit(1)
        else:
            return resource

    def load(self, **kwargs):
        """Loads stubs from info file

        Args:
            stub_list (dict): Dict of Stubs
        """
        stubs = kwargs.get('stubs', self.data.get('stubs', self.stubs))
        for name, location in stubs.items():
            _path = self.path / location
            if Path(_path).exists():
                yield self.stub_manager.add(_path)
            else:
                yield self.stub_manager.add(name)

    def create(self):
        self.log.info(
            f"Stubs: $[{' '.join(str(s) for s in self.stubs)}]")
        return self.stubs

    def update(self):
        pass

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
        self.load(stubs=stubs)
        self.log.info("Updating Project Info...")
        self.parent.to_json()
        self.log.info(
            f"Project Stubs: $[{' '.join(str(s) for s in self.stubs)}]")
        self.log.success("\nProject Updated!")
        return self.stubs
