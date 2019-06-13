# -*- coding: utf-8 -*-

"""Module for handling jinja2 and MicroPy Templates"""

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import json


class Template:
    """Generic Template Builder

    :param jinja2.Template template: Jinja Template Instance
    """
    FILENAME = None

    def __init__(self, template, **kwargs):
        self.template = template
        self.stubs = kwargs.get("stubs", None)

    @property
    def context(self):
        """Context for template"""
        raise NotImplementedError

    def render_stream(self):
        """Returns template stream from context"""
        stream = self.template.stream(self.context)
        return stream


class GenericTemplate(Template):
    """Generic Template for files without context"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FILENAME = self.template.name

    @property
    def context(self):
        """Empty Context"""
        return {}


class CodeTemplate(Template):
    """Template for VSCode settings"""
    FILENAME = ".vscode/settings.json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def context(self):
        """VScode Config Context"""
        stubs = [str(s.path) for s in self.stubs]
        stub_paths = json.dumps(stubs)
        ctx = {
            "stubs": self.stubs,
            "paths": stub_paths
        }
        return ctx


class PylintTemplate(Template):
    """Template for Pylint settings"""
    FILENAME = ".pylintrc"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def context(self):
        """Pylint Config Context"""
        ctx = {
            "stubs": self.stubs
        }
        return ctx


class TemplateProvider:
    """Template Factory"""
    _templates = {
        'vscode': CodeTemplate,
        'pylint': PylintTemplate,
        'pymakr': "pymakr.conf",
        'main': "src/main.py",
        'boot': "src/boot.py"
    }
    ENVIRONMENT = None
    TEMPLATE_DIR = Path(__file__).parent / 'template'

    def __init__(self):
        if self.__class__.ENVIRONMENT is None:
            loader = FileSystemLoader(str(self.TEMPLATE_DIR))
            self.__class__.ENVIRONMENT = Environment(loader=loader)

    def get(self, name, *args, **kwargs):
        """Retrieve appropriate Template instance by name

         :param str name: Template name to retrieve
         """
        temp_def = self._templates.get(name)
        file_attr = getattr(temp_def, "FILENAME", None)
        filename = temp_def if file_attr is None else file_attr
        temp_cls = GenericTemplate if file_attr is None else temp_def
        file_temp = self.ENVIRONMENT.get_template(filename)
        template = temp_cls(file_temp, *args, **kwargs)
        return template

    def render_to(self, name, parent_dir, *args, **kwargs):
        """Renders Template to a file under parent directory

         :param str name: Template Name to render
         :param pathlib.Path: Path object of Target Parent Directory
         """
        template = self.get(name, *args, **kwargs)
        parent_dir.mkdir(exist_ok=True)
        out_dir = parent_dir / template.FILENAME
        out_dir.parent.mkdir(exist_ok=True, parents=True)
        stream = template.render_stream()
        return stream.dump(str(out_dir))
