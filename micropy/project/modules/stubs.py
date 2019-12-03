# -*- coding: utf-8 -*-

"""Project Stubs Module."""

import sys
from pathlib import Path
from typing import List, Sequence, Union

from boltons import setutils

from micropy.project.modules import ProjectModule
from micropy.stubs import StubManager
from micropy.stubs.stubs import DeviceStub


class StubsModule(ProjectModule):
    """Project module for handling Stubs.

    Args:
        stub_manager (StubManager): StubManager instance.
        stubs (List[Type[Stub]], optional): Initial Stubs to use.

    """
    PRIORITY: int = 9

    def __init__(self, stub_manager: StubManager,
                 stubs: Sequence[DeviceStub] = None, **kwargs):
        super().__init__(**kwargs)
        self.stub_manager: StubManager = stub_manager
        self._stubs: Sequence[DeviceStub] = stubs or []

    @property
    def context(self):
        """Component stub context."""
        stub_paths = self.get_stub_tree()
        return {
            "stubs": self.stubs,
            "paths": stub_paths,
            "datadir": self.parent.data_path,
        }

    @property
    def config(self) -> dict:
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
    def stubs(self) -> Union[StubManager, Sequence[DeviceStub]]:
        """Component stubs.

        Returns:
            List[micropy.stubs.Stub]: List of stubs used in project.

        """
        _stubs = self.parent.context.get("stubs", self._stubs)
        return self._resolve_subresource(_stubs)

    @stubs.setter
    def stubs(self, value):
        """Sets project stubs.

        Args:
            val (List[micropy.stubs.Stub]): List of stubs to set.

        """
        self._stubs = value
        self.parent.context.set("stubs", self._stubs)
        self.parent.context.set("paths", self.get_stub_tree())
        self.parent.config.set("stubs", {s.name: s.stub_version for s in self._stubs})
        return self._stubs

    def get_stub_tree(self) -> Sequence[Path]:
        """Retrieve and order paths to base stubs and any stubs they depend on.

        Returns:
            Paths to all stubs project depends on.

        """
        stub_tree = setutils.IndexedSet()
        base_stubs = setutils.IndexedSet([s.stubs for s in self.stubs])
        frozen = [s.frozen for s in self.stubs]
        fware_mods = [s.firmware.frozen
                      for s in self.stubs if s.firmware is not None]
        stub_tree.update(*frozen, *fware_mods, *base_stubs)
        return stub_tree

    def _resolve_subresource(self,
                             stubs: List[DeviceStub]) -> Union[StubManager, Sequence[DeviceStub]]:
        """Resolves stub resource.

        Args:
            stubs (stubs): Stubs Passed to Manager

        """
        if not hasattr(self, "_parent"):
            return self._stubs
        if not self.parent.exists:
            return self._stubs
        try:
            resource = set(
                self.stub_manager.resolve_subresource(stubs,
                                                      self.parent.data_path))
        except OSError as e:
            self.log.error("Failed to Create Stub Links!", exception=e)
            sys.exit(1)
        else:
            return resource

    def _load_stub_data(self, stub_data=None, **kwargs):
        """Loads Serialized Stub Data.

        Args:
            stub_data (dict): Dict of Stubs

        """
        for name, location in stub_data.items():
            _path = Path(location).absolute()
            if Path(_path).exists():
                yield self.stub_manager.add(_path)
            yield self.stub_manager.add(name)

    def load(self, **kwargs):
        """Loads stubs from info file.

        Args:
            stub_list (dict): Dict of Stubs

        """
        stub_data = self.parent.config.get('stubs')
        stubs = list(self._load_stub_data(stub_data=stub_data))
        stubs.extend(self.stubs)
        self.stubs = self._resolve_subresource(stubs)
        return self.update()

    def create(self):
        """Create stub project files."""
        self.parent.context.merge(self.context)
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
        self.log.info(
            f"Project Stubs: $[{' '.join(str(s) for s in self.stubs)}]")
        self.log.success("\nProject Updated!")
        return self.stubs
