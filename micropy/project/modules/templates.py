# -*- coding: utf-8 -*-

"""Project Templates Module"""

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
from micropy.project.modules import ProjectModule
from micropy.project.template import TemplateProvider


class TemplatesModule(ProjectModule):

    def __init__(self, templates, **kwargs):
        self.templates = templates
        self.enabled = {
            'vscode': False,
            'pylint': False
        }
        self.log = Log.add_logger(
            'Templater', show_title=False)
        for key in self.enabled:
            if key in templates:
                self.enabled[key] = True
        self.provider = TemplateProvider(templates, log=self.log, **kwargs)

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
