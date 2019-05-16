"""
    MicroPy Project
"""

from pathlib import Path


class Project:
    STUB_DIR = Path.home() / '.pylint' / 'stubs'

    def __init__(self, project_name, **kwargs):
        self.name = project_name
        self.path = Path.cwd() / self.name
        print(self.STUB_DIR)
        if(self.path.exists()):
            raise Exception(f"Project {self.name} Already Exists!")
