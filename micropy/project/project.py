# -*- coding: utf-8 -*-

"""Hosts functionality relating to generation of user projects."""

from pathlib import Path

from micropy.logger import Log
from micropy.project.template import TemplateProvider
from micropy.stubs import StubManager


class Project:
    """Handles Project file generation and modification

    :param str project_name: name of project
    :param [micropy.stubs.Stub] stubs: Stubs to use in project

    """

    def __init__(self, project_name, stubs, **kwargs):
        self.path = Path(project_name).resolve()
        self.data = self.path / '.micropy'
        self.name = self.path.name
        self._stubs = stubs
        self.stubs = None
        self.log = Log.add_logger(self.name, show_title=False)
        template_log = Log.add_logger("Templater", parent=self.log)
        self.provider = TemplateProvider(log=template_log)
        self.log.info(f"Initiating $[{self.name}]")

    @property
    def context(self):
        """Get complete project context"""
        frozen = [s.frozen for s in self.stubs]
        fware_mods = [s.firmware.frozen
                      for s in self.stubs if s.firmware is not None]
        stub_paths = [s.stubs for s in self.stubs]
        paths = [*fware_mods, *frozen, *stub_paths]
        return {
            "stubs": self.stubs,
            "paths": paths,
            "datadir": self.data
        }

    def render_all(self):
        """Renders all project files"""
        self.log.info("Populating Stub info...")
        for t in self.provider.templates:
            self.provider.render_to(t, self.path, **self.context)
        self.log.success("Stubs Injected!")
        return self.context

    def create(self):
        """creates a new project"""
        self.log.info("Rendering Project files...")
        self.data.mkdir(exist_ok=True, parents=True)
        self.stubs = StubManager.resolve_subresource(self._stubs, self.data)
        self.log.debug(f"Generated Project Context: {self.context}")
        self.render_all()
        self.log.success(f"Project Created!")
        return self.path.relative_to(Path.cwd())
