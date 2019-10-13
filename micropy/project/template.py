# -*- coding: utf-8 -*-

"""Module for handling jinja2 and MicroPy Templates"""

import json
from itertools import chain
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from micropy.logger import Log

from .checks import TEMPLATE_CHECKS


class Template:
    """Base Template Builder Class

    Args:
        template (jinja2.Template): Jinja2 Template Instance

    Raises:
        NotImplementedError: Method must be overriden by subclass
    """
    FILENAME = None
    CHECKS = []

    def __init__(self, template, **kwargs):
        self.template = template
        self.stubs = kwargs.get("stubs", None)
        self.paths = kwargs.get("paths", None)
        self.datadir = kwargs.get("datadir", None)

    @property
    def context(self):
        """Context for template"""
        raise NotImplementedError

    def iter_clean(self, data=None):
        """Yields cleaned data

        Args:
            data (str, optional): Alternative data to clean.
                Defaults to None. If none, uses template render.
        """
        render = data or self.template.render(self.context)
        for line in render.splitlines(True):
            _line = line.strip()
            if not _line.startswith("//"):
                yield line

    def run_checks(self):
        """Runs all template checks

        Returns:
            bool: True if all checks passed
        """
        if not self.CHECKS:
            return True
        results = [not ck() for ck in self.CHECKS]
        return any(results)

    def update(self, root):
        """Update Template File

        Args:
            root (str): Path to project root

        Raises:
            NotImplementedError: Raised if Subclass has not Implemented Update

        Returns:
            func: Template Update Func
        """
        update_func = getattr(self, 'update_method', None)
        update_kwargs = getattr(self, 'update_kwargs', {})
        if not update_func:
            return None
        path = root / self.FILENAME
        return update_func(path, **update_kwargs)

    def update_as_json(self, path):
        """Update template file as JSON

        Args:
            path (str): File path to update
        """
        render = json.loads("".join(self.iter_clean()))
        data = json.loads("".join(self.iter_clean(path.read_text())))
        data.update(render)
        with path.open('w+') as f:
            json.dump(data, f, indent=4)

    def update_as_text(self, path, by_contains=None):
        """Update template file as text

        Args:
            path (str): file path to update.
            by_contains ([str], optional): Update lines that contain a string.
             Defaults to None.
        """
        r_lines = list(self.iter_clean())
        upd_lines = []
        if by_contains:
            upd_lines = [r_lines.index(l) for l in r_lines if any(
                i in l for i in by_contains)]
        with path.open('r+') as f:
            c_lines = self.iter_clean(f.read())
            f.seek(0)
            for it, line in enumerate(c_lines):
                _line = line
                if it in upd_lines:
                    _line = r_lines[it]
                f.write(_line)

    def render_stream(self):
        """Returns template stream from context"""
        stream = self.template.stream(self.context)
        return stream

    def __str__(self):
        cls_name = self.__class__.__name__
        return f"{cls_name}[{self.template.name}]::[{self.context}]"


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
    CHECKS = [
        TEMPLATE_CHECKS['ms-python']
    ]

    def __init__(self, *args, **kwargs):
        self.update_method = self.update_as_json
        super().__init__(*args, **kwargs)

    @property
    def context(self):
        """VScode Config Context"""
        if self.datadir:
            paths = [str(p.relative_to(self.datadir.parent))
                     for p in self.paths]
        stub_paths = json.dumps(paths)
        ctx = {
            "stubs": self.stubs,
            "paths": stub_paths,
        }
        return ctx


class PylintTemplate(Template):
    """Template for Pylint settings"""
    FILENAME = ".pylintrc"

    def __init__(self, *args, **kwargs):
        self.update_method = self.update_as_text
        self.update_kwargs = {'by_contains': ['sys.path.insert']}
        super().__init__(*args, **kwargs)

    @property
    def context(self):
        """Pylint Config Context"""
        if self.datadir:
            paths = [p.relative_to(self.datadir.parent) for p in self.paths]
        ctx = {
            "stubs": self.stubs,
            "paths": paths
        }
        return ctx


class TemplateProvider:
    """Template Factory"""
    _template_files = {
        'vscode': CodeTemplate,
        'pylint': PylintTemplate,
        'pymakr': "pymakr.conf",
        'main': "src/main.py",
        'boot': "src/boot.py",
        'gitignore': ".gitignore"
    }
    ENVIRONMENT = None
    TEMPLATE_DIR = Path(__file__).parent / 'template'
    TEMPLATES = {
        'vscode': (['vscode'], ("VSCode Settings for "
                                "Autocompletion/Intellisense")),
        'pymakr': (['pymakr'], "Pymakr Configuration"),
        'pylint': (['pylint'], "Pylint MicroPython Settings"),
        'gitignore': (['gitignore'], "Git Ignore Template"),
        'bootstrap': (['main', 'boot'], "main.py & boot.py files")
    }

    def __init__(self, templates, log=None, **kwargs):
        """Template Factory

        Args:
            templates ([str]): List of Templates to use
            log (callable, optional): Log instance to use.
                Defaults to None. If none, creates a new one.
            run_checks (bool, optional): Whether to run template checks.
                Defaults to True.
        """
        self.run_checks = kwargs.get('run_checks', True)
        self.template_names = set(chain.from_iterable(
            [self.TEMPLATES.get(t)[0] for t in templates]))
        self.files = {k: v for k, v in self._template_files.items()
                      if k in self.template_names}
        self.log = log or Log.add_logger('Templater')
        if self.__class__.ENVIRONMENT is None:
            loader = FileSystemLoader(str(self.TEMPLATE_DIR))
            self.__class__.ENVIRONMENT = Environment(loader=loader)
            self.log.debug("Created Jinja2 Environment")
            self.log.debug(
                f"Detected Templates: {self.ENVIRONMENT.list_templates()}")

    def get(self, name, *args, **kwargs):
        """Retrieve appropriate Template instance by name

        Args:
            name (str): Name of template

        Returns:
            Template: Template instance
        """
        temp_def = self.files.get(name)
        file_attr = getattr(temp_def, "FILENAME", None)
        filename = temp_def if file_attr is None else file_attr
        temp_cls = GenericTemplate if file_attr is None else temp_def
        file_temp = self.ENVIRONMENT.get_template(filename)
        self.log.debug(
            f"Retrieving {name} as {temp_cls} from {file_temp.name}")
        template = temp_cls(file_temp, *args, **kwargs)
        return template

    def render_to(self, name, parent_dir, *args, **kwargs):
        """Renders Template to a file under parent directory

        Args:
            name (str): Name of template
            parent_dir (str): Path to root dir
        """
        template = self.get(name, **kwargs)
        self.log.debug(f"Loaded: {str(template)}")
        if self.run_checks:
            self.log.debug(f"Verifying {template} requirements...")
            template.run_checks()
        parent_dir.mkdir(exist_ok=True)
        out_dir = parent_dir / template.FILENAME
        out_dir.parent.mkdir(exist_ok=True, parents=True)
        self.log.debug(f"Rendered: {name} to {str(out_dir)}")
        self.log.info(f"$[{name.capitalize()}] File Generated!")
        stream = template.render_stream()
        return stream.dump(str(out_dir))

    def update(self, name, root_dir, **kwargs):
        """Update existing Template

        Args:
            name (str): Template name
            root_dir (str): Path to project root

        Returns:
            Template: Updated Template Instance
        """
        template = self.get(name, **kwargs)
        self.log.debug(f"Loaded: {str(template)}")
        try:
            template.update(root_dir)
        except FileNotFoundError:
            self.log.debug("Template does not exist!")
            return self.render_to(name, root_dir, **kwargs)
        self.log.debug(f"Updated: {str(template)}")
        return template

    @property
    def templates(self):
        """returns all template names"""
        return self.files.keys()
