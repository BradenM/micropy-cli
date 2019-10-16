# -*- coding: utf-8 -*-

"""Project Templates Module"""


from micropy.logger import Log
from micropy.project.modules import ProjectModule
from micropy.project.template import TemplateProvider


class TemplatesModule(ProjectModule):
    TEMPLATES = TemplateProvider.TEMPLATES

    def __init__(self, templates=None, run_checks=True, **kwargs):
        self.templates = templates or []
        self.run_checks = run_checks
        self.enabled = {
            'vscode': False,
            'pylint': False
        }
        self.log = Log.add_logger(
            'Templater', show_title=False)
        if templates:
            for key in self.enabled:
                if key in self.templates:
                    self.enabled[key] = True
            self.provider = TemplateProvider(
                templates, run_checks=self.run_checks, log=self.log, **kwargs)

    @property
    def config(self):
        return {
            'config': self.enabled
        }

    def load(self, **kwargs):
        templates = [k for k, v in self.parent.config.items() if v]
        self.provider = TemplateProvider(templates, **kwargs)

    def create(self):
        self.log.title("Rendering Templates")
        self.log.info("Populating Stub Info...")
        for t in self.provider.templates:
            self.provider.render_to(t, self.parent.path, **self.parent.context)
        self.log.success("Stubs Injected!")
        return self.parent.context

    def update(self):
        for tmp in self.provider.templates:
            self.provider.update(tmp, self.parent.path, **self.parent.context)
        return self.parent.context
