# -*- coding: utf-8 -*-

"""Hosts functionality relating to generation of user projects."""

from pathlib import Path

from cookiecutter.generate import generate_files

from micropy.logger import Log
from micropy.main import MicroPy

import json


class Project:
    """Handles Project file generation and modification

    :param str project_name: name of project

    """

    def __init__(self, project_name, stubs, **kwargs):
        self.path = Path.cwd() / project_name
        self.name = self.path.name
        self.stubs = stubs
        self.log = Log().add_logger(self.name, 'cyan')
        super().__init__()

    @property
    def context(self):
        """get project context"""
        stub_ctx = {str(i): {"path": str(i.path)} for i in self.stubs}
        proj_ctx = {
            "project": self.name,
            "pylint": stub_ctx,
            "vscode": [str(i.path) for i in self.stubs],
        }
        self.log.debug(f"Generated Project Context: {proj_ctx}")
        return proj_ctx

    def cookie_ctx(self):
        """wraps context with needed items for cookiecutter"""
        proj_ctx = self.context.copy()
        cookie_ctx = {'cookiecutter': proj_ctx}
        cookie_ctx['cookiecutter']['_template'] = MicroPy.TEMPLATE
        return cookie_ctx

    def write_vscode(self):
        """write json to vscode settings.json"""
        cfg_path = self.path / '.vscode' / 'settings.json'
        cfg = json.loads(cfg_path.read_text())
        with cfg_path.open('w+') as cfg_file:
            stub_cfgs = {key: self.context['vscode']
                         for key, v in cfg.items() if type(v) is list}
            cfg.update(stub_cfgs)
            self.log.debug(f"VSCode Rendered Settings: {cfg}")
            json.dump(cfg, cfg_file)
            return cfg

    def create(self):
        """creates a new project"""
        self.log.info(f"Initiating $[{self.name}]")
        generate_files(str(MicroPy.TEMPLATE), context=self.cookie_ctx(),
                       output_dir=str(Path.cwd()))
        self.log.info("Populating Stub info...")
        self.write_vscode()
        self.log.success("Stubs Injected!")
        self.log.success("Project Initiated!")
