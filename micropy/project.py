#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pathlib import Path
from string import Template
from shutil import copytree, copy2
from micropy.logger import ServiceLog
import questionary as prompt


class Project:
    TEMPLATE = Path(__file__).parent / 'template'
    FILES = Path.home() / '.micropy'
    STUB_DIR = FILES / 'stubs'

    def __init__(self, project_name, **kwargs):
        """Handles Project file generation and modification

        Args:
            project_name (string): name of project

        """
        self.path = Path.cwd() / project_name
        self.name = self.path.name
        self.log = ServiceLog(self.name, 'bright_blue')

    def setup(self):
        if not self.FILES.exists():
            self.log.info("Missing .micropy folder, creating now...")
            self.FILES.mkdir()
        if not self.STUB_DIR.exists():
            e = Exception('You have no stubs!')
            self.log.exception(e)
            self.log.error("Please run micropy stub get")
            raise e

    def add_stub(self, path):
        stub_path = Path(path)
        out = self.STUB_DIR / stub_path.name
        self.log.info(f"Adding $[{stub_path.name}] to stubs...")
        copytree(stub_path, out)
        self.log.success("Done!")

    def copy_file(self, src, dest):
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
        content = path.read_text()
        temp = Template(content)
        output = temp.substitute(**kwargs)
        path.write_text(output)
        return output

    def load_stubs(self):
        vs_path = self.path / '.vscode' / 'settings.json'
        pylint_path = self.path / '.pylintrc'
        stubs = list(self.STUB_DIR.iterdir())
        vs_stubs = [f'"{s}"' for s in stubs]
        self.log.info(f"Found $[{len(stubs)}] stubs, injecting...")
        lint_stubs = prompt.checkbox(
            "Which stubs would you like pylint to load?", choices=[i.name for i in stubs]).ask()
        pylint_stubs = [
            f'sys.path.insert(1,"{stub}")' for stub in stubs if stub.name in lint_stubs]
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
        self.log.info(f"Refreshing Stubs for $[{self.name}]")
        vs_temp = self.TEMPLATE / 'dotvscode' / 'settings.json'
        pylint_temp = self.TEMPLATE / 'dotpylintrc'
        vs_path = self.path / '.vscode' / 'settings.json'
        pylint_path = self.path / '.pylintrc'
        copy2(vs_temp, vs_path)
        copy2(pylint_temp, pylint_path)
        return self.load_stubs()

    def create(self):
        self.log.info(f"Initiating $[{self.name}]")
        copytree(self.TEMPLATE, self.path, copy_function=self.copy_file)
        vs_old = self.path / 'dotvscode'
        vs_old.rmdir()
        self.log.success("Files Loaded!")
        self.log.info("Populating Stub info...")
        self.load_stubs()
        self.log.success("Project Initiated!")
