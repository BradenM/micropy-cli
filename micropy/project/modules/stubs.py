# -*- coding: utf-8 -*-

"""Project Stubs Module."""

import sys
from pathlib import Path

from boltons import setutils

from micropy.exceptions import StubError
from micropy.project.modules import ProjectModule


class StubsModule(ProjectModule):
    """Project module for handling Stubs.

    Args:
        stub_manager (micropy.stubs.StubManager): StubManager instance.
        stubs (List[micropy.stubs.Stub]): Initial Stubs to use.

    """

    def __init__(self, stub_manager, stubs=None):
        self.stub_manager = stub_manager
        self._stubs = stubs or []

    @property
    def context(self):
        """Component stub context."""
        paths = setutils.IndexedSet()
        if self.stubs:
            frozen = [s.frozen for s in self.stubs]
            fware_mods = [s.firmware.frozen
                          for s in self.stubs if s.firmware is not None]
            stub_paths = [s.stubs for s in self.stubs]
            paths.update(*frozen, *fware_mods, *stub_paths)

        return {
            "stubs": set(self.stubs),
            "paths": paths,
            "datadir": self.parent.data_path,
        }

    @property
    def config(self):
        """Component specific config values.

        Returns:
            dict: Current config.

        """
        stubs = {s.name: s.stub_version for s in self._stubs}
        return {
            'stubs': stubs
        }

    @property
    @ProjectModule.hook()
    def stubs(self):
        """Component stubs.

        Returns:
            List[micropy.stubs.Stub]: List of stubs used in project.

        """
        return self._resolve_subresource(self._stubs)

    @stubs.setter
    def stubs(self, val):
        """Sets project stubs.

        Args:
            val (List[micropy.stubs.Stub]): List of stubs to set.

        """
        self._stubs = val

    def _resolve_subresource(self, stubs):
        """Resolves stub resource.

        Args:
            stubs (stubs): Stubs Passed to Manager

        """
        if not hasattr(self, "_parent"):
            return self._stubs
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

    def _load_stub_data(self, stub_data=None, **kwargs):
        """Loads Serialized Stub Data.

        Args:
            stub_data (dict): Dict of Stubs

        """
        _data = self.config['stubs']
        data = {**stub_data, **_data}
        for name, location in data.items():
            _path = Path(location).absolute()
            if Path(_path).exists():
                yield self.stub_manager.add(_path)
            yield self.stub_manager.add(name)

    def load(self, **kwargs):
        """Loads stubs from info file.

        Args:
            stub_list (dict): Dict of Stubs

        """
        stub_data = self.parent.data.get('stubs', {})
        stubs = list(self._load_stub_data(stub_data=stub_data))
        stubs.extend(self.stubs)
        self.stubs = self._resolve_subresource(stubs)
        return self.stubs

    def create(self):
        """Create stub project files."""
        self.log.info(
            f"Stubs: $[{' '.join(str(s) for s in self.stubs)}]")
        return self.load()

    def update(self):
        """Update current project stubs."""
        self.stubs = self.load()
        return self.stubs

    @ProjectModule.hook()
    def add_stub(self, stub, **kwargs):
        """Add stub to project.

        Args:
            stub (Stub): Stub object to add

        Returns:
            [Stubs]: Project Stubs

        """
        loaded = self.stubs or []
        stubs = [*loaded, stub]
        self.log.info("Loading project...")
        self.stubs = self._resolve_subresource(stubs)
        self.log.info("Updating Project Info...")
        self.parent.update()
        self.parent.to_json()
        self.log.info(
            f"Project Stubs: $[{' '.join(str(s) for s in self.stubs)}]")
        self.log.success("\nProject Updated!")
        return self.stubs
