# -*- coding: utf-8 -*-

"""Hosts functionality relating to generation of user projects."""

from pathlib import Path
from shutil import copy2, copytree
from string import Template

import questionary as prompt

from micropy import LOG
from micropy.main import MicroPy


class Project:
    """Handles Project file generation and modification

    :param str project_name: name of project

    """

    def __init__(self, project_name, **kwargs):
        self.path = Path.cwd() / project_name
        self.name = self.path.name
        self.log = LOG.add_logger(self.name, 'bright_blue')
        super().__init__()

    def copy_file(self, src, dest):
        """Helper function to parse 'dots' out of template names

        :param str src: file source
        :param str dest: file destination

        """
        file = Path(src)
        filename = file.name
        parent = file.parent
        if filename[:3] == 'dot':
            name = filename[3:]
            out = f'.{name}'
            dest = Path(dest).parent / out
        if parent.name[:3] == 'dot':
            parent_name = parent.name[3:]
            out = f'.{parent_name}'
            out_dir = Path(dest).parent.parent / out
            out_dir.mkdir(parents=True, exist_ok=True)
            dest = out_dir / filename
        return copy2(src, dest)

    def load_template(self, path, **kwargs):
        """Renders a template

        :param str path: path to template
        :param **kwargs:
        :return: rendered text
        :rtype: str

        """
        content = path.read_text()
        temp = Template(content)
        output = temp.substitute(**kwargs)
        path.write_text(output)
        return output

    def load_stubs(self):
        """loads stubs into templates"""
        vs_path = self.path / '.vscode' / 'settings.json'
        pylint_path = self.path / '.pylintrc'
        stubs = MicroPy.STUBS
        vs_stubs = [f'"{s.path}"' for s in stubs]
        self.log.info(f"Found $[{len(stubs)}] stubs, injecting...")
        lint_stubs = prompt.checkbox(
            "Which stubs would you like pylint to load?", choices=[str(i) for i in stubs]).ask()
        pylint_stubs = [
            f'sys.path.insert(1,"{str(stub.path)}")' for stub in stubs if str(stub) in lint_stubs]
        vscode_sub = {
            'stubs': ',\n'.join(vs_stubs)
        }
        pylint_sub = {
            'stubs': ';'.join(pylint_stubs)
        }
        self.load_template(vs_path, **vscode_sub)
        self.load_template(pylint_path, **pylint_sub)
        self.log.success("Stubs Loaded!")

    def refresh_stubs(self):
        """refreshes project with new stubs"""
        self.log.info(f"Refreshing Stubs for $[{self.name}]")
        vs_temp = MicroPy.TEMPLATE / 'dotvscode' / 'settings.json'
        pylint_temp = MicroPy.TEMPLATE / 'dotpylintrc'
        vs_path = self.path / '.vscode' / 'settings.json'
        pylint_path = self.path / '.pylintrc'
        copy2(vs_temp, vs_path)
        copy2(pylint_temp, pylint_path)
        return self.load_stubs()

    def create(self):
        """creates a new project"""
        self.log.info(f"Initiating $[{self.name}]")
        copytree(MicroPy.TEMPLATE, self.path, copy_function=self.copy_file)
        vs_old = self.path / 'dotvscode'
        vs_old.rmdir()
        self.log.success("Files Loaded!")
        self.log.info("Populating Stub info...")
        self.load_stubs()
        self.log.success("Project Initiated!")
