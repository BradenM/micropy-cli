#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pathlib import Path
from string import Template
from shutil import copytree, copy2


class Project:
    TEMPLATE = Path(__file__).parent / 'template'
    STUB_DIR = Path.home() / '.micropy' / 'stubs'

    def __init__(self, project_name, **kwargs):
        """Handles Project file generation and modification

        Args:
            project_name (string): name of project

        """
        self.name = project_name
        self.path = Path.cwd() / self.name
        self.create(self.path)

    def copy_file(self, src, dest):
        file = Path(src)
        filename = file.name
        parent = file.parent
        print(src)
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
        print(dest)
        print("\n")
        return copy2(src, dest)

    def load_template(self, path, **kwargs):
        content = path.read_text()
        temp = Template(content)
        output = temp.substitute(**kwargs)
        path.write_text(output)
        return output

    def create(self, path):
        copytree(self.TEMPLATE, self.path, copy_function=self.copy_file)
        vs_path = self.path / '.vscode' / 'settings.json'
        pylint_path = self.path / '.pylintrc'
        vs_old = self.path / 'dotvscode'
        vs_old.rmdir()
        stubs = [f'"{s}"' for s in list(self.STUB_DIR.iterdir())]
        esp_stub = next(self.STUB_DIR.glob("esp32_1_10*"))
        print(stubs)
        vscode_sub = {
            'stubs': ',\n'.join(stubs)
        }
        pylint_sub = {
            'stub': str(esp_stub.resolve())
        }
        self.load_template(vs_path, **vscode_sub)
        self.load_template(pylint_path, **pylint_sub)
