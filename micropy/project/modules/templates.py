# -*- coding: utf-8 -*-

"""Project Templates Module."""


from micropy.logger import Log
from micropy.project.modules import ProjectModule
from micropy.project.template import TemplateProvider


class TemplatesModule(ProjectModule):
    """Project Templates Module.

    Generates and manages project files using the Projects
    context.

    Args:
        templates (List[str]): List of templates to use.
        run_checks (bool, optional): Whether to execute checks or not.
            Defaults to True.

    """
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
        """Template config.

        Returns:
            dict: Current configuration

        """
        return {
            'config': self.enabled
        }

    def load(self, **kwargs):
        """Loads project templates."""
        _data = self.parent.data.get('config', {})
        self.enabled = {**self.enabled, **_data}
        templates = [k for k, v in self.enabled.items() if v]
        self.log.debug(f"Loading Templates: {templates}")
        self.provider = TemplateProvider(templates, **kwargs)
        self.update()

    def create(self):
        """Generates project files.

        Returns:
            dict: Project context

        """
        self.log.title("Rendering Templates")
        self.log.info("Populating Stub Info...")
        for t in self.provider.templates:
            self.provider.render_to(t, self.parent.path, **self.parent.context)
        self.log.success("Stubs Injected!")
        return self.parent.context

    def update(self):
        """Updates project files.

        Returns:
            dict: Project context

        """
        for tmp in self.provider.templates:
            self.provider.update(tmp, self.parent.path, **self.parent.context)
        return self.parent.context
