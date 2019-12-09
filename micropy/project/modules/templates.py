# -*- coding: utf-8 -*-

"""Project Templates Module."""


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
    PRIORITY: int = 1
    TEMPLATES = TemplateProvider.TEMPLATES
    _dynamic = ['vscode', 'pylint']

    def __init__(self, templates=None, run_checks=True, **kwargs):
        self._templates = templates or []
        super().__init__(**kwargs)
        self.run_checks = run_checks

    @property
    def config(self):
        """Template config.

        Returns:
            dict: Current configuration

        """
        return self.parent.config

    def get_provider(self, templates):
        return TemplateProvider(templates, run_checks=self.run_checks, log=self.log)

    def load(self, **kwargs):
        """Loads project templates."""
        self.provider = self.get_provider(self.config.get('config'))
        templates = [k for k, v in self.config.get('config').items() if v]
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
        for key in self._templates:
            if key in self._dynamic:
                self.config.add('config' + '/' + key, True)
        self.provider = self.get_provider(self._templates)
        for t in self.provider.templates:
            self.provider.render_to(t, self.parent.path, **self.parent.context.raw())
        self.log.success("Stubs Injected!")
        return self._templates

    def update(self):
        """Updates project files.

        Returns:
            dict: Project context

        """
        self.provider = self.get_provider(self.config.get('config'))
        self.log.debug(f"updating templates with context: {self.parent.context.raw()}")
        for tmp in self.provider.templates:
            self.provider.update(tmp, self.parent.path, **self.parent.context.raw())
        return self.parent.context
