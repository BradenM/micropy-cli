#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pathlib import Path


class Project:
    STUB_DIR = Path.home() / '.pylint' / 'stubs'

    def __init__(self, project_name, **kwargs):
        """Handles Project file generation and modification
        
        Args:
            project_name (string): name of project
        
        """
        self.name = project_name
        self.path = Path.cwd() / self.name
        print(self.STUB_DIR)