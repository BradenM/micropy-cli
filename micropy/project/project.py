# -*- coding: utf-8 -*-

"""Hosts functionality relating to generation of user projects."""

from pathlib import Path


from micropy.logger import Log
from micropy.project.template import TemplateProvider


class Project:
    """Handles Project file generation and modification

    :param str project_name: name of project
    :param [micropy.stubs.Stub] stubs: Stubs to use in project

    """

    def __init__(self, project_name, stubs, **kwargs):
        self.path = Path(project_name).resolve()
        self.name = self.path.name
        self.stubs = stubs
        log = Log()
        self.log = log.add_logger(self.name, 'cyan')
        template_log = log.add_logger("Templater", parent=self.log)
        self.provider = TemplateProvider(log=template_log)
        self.log.info(f"Initiating $[{self.name}]")

    @property
    def context(self):
        """Get complete project context"""
        return {
            "stubs": self.stubs
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
        self.log.debug(f"Generated Project Context: {self.context}")
        self.log.info("Rendering Project files...")
        self.render_all()
        self.log.success(f"Project Created!")
        return self.path.relative_to(Path.cwd())
