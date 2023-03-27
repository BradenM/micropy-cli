from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import List, Optional, cast

import micropy.exceptions as exc
import questionary as prompt
import typer
from micropy import logger, utils
from micropy.main import MicroPy
from micropy.project import Project, modules
from micropy.stubs.stubs import Stub
from questionary import Choice

from .stubs import stubs_app

app = typer.Typer(name="micropy-cli", no_args_is_help=True, rich_markup_mode="markdown")
app.add_typer(stubs_app)


@app.callback()
def main_callback(ctx: typer.Context):
    """
    **Micropy CLI** is a project management/generation tool for writing [Micropython](https://micropython.org/) code in modern IDEs such as VSCode.

    Its primary goal is to automate the process of creating a workspace complete with:

    * **Linting** compatible with Micropython

    * IDE **Intellisense**

    * **Autocompletion**

    * Dependency Management

    * VCS Compatibility
    """
    if ctx.resilient_parsing:
        return
    micropy = ctx.ensure_object(MicroPy)
    if not micropy.project.exists:
        return
    latest = utils.is_update_available()
    if latest:
        log = logger.Log.get_logger("MicroPy")
        log.title("Update Available!")
        log.info(f"Version $B[v{latest}] is now available")
        log.info("You can update via: $[pip install --upgrade micropy-cli]\n")


TemplateEnum = Enum(
    "TemplateEnum", {t: t for t in list(modules.TemplatesModule.TEMPLATES.keys())}, type=str
)


def template_callback(
    ctx: typer.Context, value: Optional[List[TemplateEnum]]
) -> Optional[List[TemplateEnum]]:
    if ctx.resilient_parsing:
        return
    if not value:
        templates = modules.TemplatesModule.TEMPLATES.items()
        templ_choices = [Choice(str(val[1]), value=t) for t, val in templates]
        value = prompt.checkbox("Choose any Templates to Generate", choices=templ_choices).ask()
        if not value:
            if not prompt.confirm(
                "You have chosen to use NO templates. Are you sure you want to continue?",
                default=False,
            ).ask():
                raise typer.Abort()
            return []
    value = [TemplateEnum(k) for k in value]
    return value


def path_callback(ctx: typer.Context, value: Optional[Path]) -> Optional[Path]:
    if ctx.resilient_parsing:
        return
    return value if value else Path.cwd()


def name_callback(ctx: typer.Context, value: Optional[str]) -> Optional[str]:
    if ctx.resilient_parsing:
        return
    if not value:
        path = ctx.params.get("path", Path.cwd())
        default_name = path.name
        prompt_name = prompt.text("Project Name", default=default_name).ask()
        if prompt_name is None:
            raise typer.Abort("You must provide a project name via prompt or --name option.")
        return prompt_name.strip()
    return value


def stubs_callback(ctx: typer.Context, value: Optional[List[str]]) -> Optional[List[Stub]]:
    if ctx.resilient_parsing:
        return
    mpy = ctx.ensure_object(MicroPy)
    stub_values = (
        [i for i in [mpy.stubs.add(s) for s in value] if i is not None]
        if value
        else list(mpy.stubs)
    )
    if not stub_values:
        mpy.log.error("You don't have any stubs!")
        mpy.log.title("To add stubs to micropy, use $[micropy stubs add <STUB_NAME>]")
        mpy.log.info("See: $[micropy stubs --help] for more information.")
        raise typer.Abort(1)
    if not value:
        # if value was not explicitly provided, ask for selections.
        stubs = [Choice(str(s), value=s) for s in stub_values]
        stub_choices = prompt.checkbox("Which stubs would you like to use?", choices=stubs).ask()
        if not stub_choices:
            # mpy.log.error("You must choose at least one stub!")
            raise typer.BadParameter(
                "You must choose at least one stub!",
                ctx,
            )
        return stub_choices
    return stub_values


@app.command(name="init")
def main_init(
    ctx: typer.Context,
    path: Optional[Path] = typer.Argument(
        None,
        help="Path to project. Defaults to current working directory.",
        callback=path_callback,
        dir_okay=True,
        file_okay=False,
        show_default=False,
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Project Name. Defaults to path name.",
        show_default=False,
        callback=name_callback,
    ),
    template: Optional[List[TemplateEnum]] = typer.Option(
        None,
        "--template",
        "-t",
        help="Templates to generate for project. Can be specified multiple times. Skips interactive prompt.",
        show_default=False,
        callback=template_callback,
    ),
    stubs: Optional[List[str]] = typer.Option(
        None,
        "--stubs",
        "-s",
        help="Name of stubs to add to project. Can be specified multiple times. Skips interactive prompt.",
        callback=stubs_callback,
        show_default=False,
    ),
):
    """Create new Micropython Project.

    \b When creating a new project, all files will be placed under the
    generated <PROJECT_NAME> folder.

    """
    mpy: MicroPy = ctx.find_object(MicroPy)
    mpy.log.title("Creating New Project")
    # weird issue where "template" from args
    # gets set a [None,None], but its correct in params.
    template = ctx.params.get("template", template)
    project = Project(path, name=name)
    project.add(modules.StubsModule, mpy.stubs, stubs=stubs)
    project.add(modules.PackagesModule, "requirements.txt")
    project.add(modules.DevPackagesModule, "dev-requirements.txt")
    project.add(
        modules.TemplatesModule,
        templates=[t.value for t in template if t],
        run_checks=mpy.RUN_CHECKS,
    )
    proj_path = project.create()
    try:
        rel_path = f"./{proj_path.relative_to(Path.cwd())}"
    except ValueError:
        rel_path = proj_path
    mpy.log.title(f"Created $w[{project.name}] at $w[{rel_path}]")


def ensure_project(ctx: typer.Context) -> Project:
    mpy = ctx.ensure_object(MicroPy)
    project = mpy.project
    if not project.exists:
        mpy.log.error("You are not currently in an active project!")
        raise typer.Abort(1)
    # todo: fix type issue.
    return cast(Project, project)


def install_local_callback(ctx: typer.Context, value: Optional[Path]) -> Optional[Path]:
    """Handle package installation from local path."""
    if ctx.resilient_parsing:
        return
    if value is None:
        return value
    mpy = ctx.ensure_object(MicroPy)
    project = ensure_project(ctx)
    pkg_name = next(iter(ctx.args), None)
    mpy.log.title("Installing Local Package")
    pkg_path = "-e " + str(value)
    project.add_package(pkg_path, dev=ctx.params.get("dev", False), name=pkg_name)
    raise typer.Exit()


def install_project_callback(ctx: typer.Context, value: Optional[List[str]]) -> Optional[List[str]]:
    """Handle project requirements install."""
    if ctx.resilient_parsing:
        return
    if "path" in ctx.params:
        return
    if not value:
        # only if no packages are provided.
        mpy = ctx.ensure_object(MicroPy)
        project = ensure_project(ctx)
        mpy.log.title("Installing all Requirements")
        try:
            project.add_from_file(dev=ctx.params.get("dev", False))
        except Exception as e:
            mpy.log.error("Failed to load requirements!", exception=e)
            raise typer.Abort() from e
        else:
            mpy.log.success("\nRequirements Installed!")
            raise typer.Exit()
    return value


@app.command(name="install")
def main_install(
    ctx: typer.Context,
    packages: Optional[List[str]] = typer.Argument(
        None, help="Packages to install.", callback=install_project_callback
    ),
    dev: bool = typer.Option(
        default=False,
        help="Install as development package. This will not generate stubs for the package.",
        show_default=True,
    ),
    path: Optional[Path] = typer.Option(
        None,
        help="Add dependency from local path. Can be a file or directory.",
        callback=install_local_callback,
    ),
):
    """Install Packages as Project Requirements.

    \b
    Install a project dependency while enabling
    intellisense, autocompletion, and linting for it.

        \b
        $ micropy install picoweb==1.8.2 blynklib
        \b



    \b
    If no packages are passed and a requirements.txt file is found,
    then micropy will install all packages listed in it.

    \b
    If the --dev flag is passed, then the packages are only
    added to micropy.json. They are not stubbed.

    \b
    To add a dependency from a path, use the --path option
    and provide a name for your package:

        \b
        $ micropy install --path ./src/lib/mypackage MyCustomPackage
        \b



    \b
    You can import installed packages just as you would
    on your actual device:

        \b
        _import <package_name>_

    """
    mpy: MicroPy = ctx.ensure_object(MicroPy)
    project = ensure_project(ctx)
    mpy.log.title("Installing Packages")
    for pkg in packages:
        try:
            project.add_package(pkg, dev=dev)
        except exc.RequirementException as e:
            pkg_name = str(e.package)
            mpy.log.error(f"Failed to install {pkg_name}!" " Is it available on PyPi?", exception=e)
            raise typer.Abort() from e
