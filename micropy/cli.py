#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""MicropyCli Console Entrypoint."""
import sys
from pathlib import Path

import click
import questionary as prompt
from questionary import Choice

import micropy.exceptions as exc
from micropy import main, utils
from micropy.logger import Log
from micropy.project import Project, modules

pass_mpy = click.make_pass_decorator(main.MicroPy, ensure=True)


@click.group(invoke_without_command=True)
@click.version_option()
@click.option('--skip-checks', '-s', is_flag=True,
              default=False, help='Skip Project Checks. Defaults to False.')
@pass_mpy
@click.pass_context
def cli(ctx, mpy, skip_checks=False):
    """CLI Application for creating/managing Micropython Projects."""
    if ctx.invoked_subcommand is None:
        if not mpy.project.exists:
            return click.echo(ctx.get_help())
    latest = utils.is_update_available()
    if latest:
        log = Log.get_logger('MicroPy')
        log.title("Update Available!")
        log.info(f"Version $B[v{latest}] is now available")
        log.info(
            "You can update via: $[pip install --upgrade micropy-cli]\n")
    mpy.RUN_CHECKS = not skip_checks


@cli.group(short_help="Manage Micropy Stubs")
def stubs():
    """Manage Micropy Stubs.

    \b
    Stub files are what enable linting,
    Intellisense, Autocompletion, and more.

    \b
    To achieve the best results, you can install
    stubs specific to your device/firmware using:

        micropy stubs add <STUB_NAME>

    For more info, please check micropy stubs add --help

    """


@cli.command(short_help="Create new Micropython Project")
@click.argument('path', required=False, default=None)
@click.option('--name', '-n', required=False, default=None,
              help="Project Name. Defaults to Path name.")
@click.option('--template', '-t',
              type=click.Choice(modules.TemplatesModule.TEMPLATES.keys()),
              multiple=True,
              required=False,
              help=("Templates to generate for project."
                    " Multiple options can be passed."))
@pass_mpy
def init(mpy, path, name=None, template=None):
    """Create new Micropython Project.

    \b When creating a new project, all files will be placed under the
    generated <PROJECT_NAME> folder.

    """
    mpy.log.title("Creating New Project")
    if not path:
        path = Path.cwd()
        default_name = path.name
        prompt_name = prompt.text("Project Name", default=default_name).ask()
        name = prompt_name.strip()
    if not template:
        templates = modules.TemplatesModule.TEMPLATES.items()
        templ_choices = [Choice(str(val[1]), value=t)
                         for t, val in templates]
        template = prompt.checkbox(
            f"Choose any Templates to Generate", choices=templ_choices).ask()
    stubs = [Choice(str(s), value=s) for s in mpy.stubs]
    if not stubs:
        mpy.log.error("You don't have any stubs!")
        mpy.log.title(
            "To add stubs to micropy, use $[micropy stubs add <STUB_NAME>]")
        sys.exit(1)
    stub_choices = prompt.checkbox(
        f"Which stubs would you like to use?", choices=stubs).ask()
    project = Project(path, name=name)
    project.add(modules.StubsModule, mpy.stubs, stubs=stub_choices)
    project.add(modules.PackagesModule, 'requirements.txt')
    project.add(modules.DevPackagesModule, 'dev-requirements.txt')
    project.add(modules.TemplatesModule, templates=template, run_checks=mpy.RUN_CHECKS)
    proj_path = project.create()
    try:
        rel_path = f"./{proj_path.relative_to(Path.cwd())}"
    except ValueError:
        rel_path = proj_path
    mpy.log.title(f"Created $w[{project.name}] at $w[{rel_path}]")


@cli.command(short_help="Install Project Requirements")
@click.argument('packages', nargs=-1)
@click.option('-d', '--dev', is_flag=True, default=False,
              help=("Add dependency to dev requirements"))
@click.option('-p', '--path', type=click.Path(exists=True, path_type=str),
              help=("Add dependency from local path. Can be a file or directory."))
@pass_mpy
def install(mpy, packages, dev=False, path=None):
    """Install Packages as Project Requirements.

    \b
    Install a project dependency while enabling
    intellisense, autocompletion, and linting for it.

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
    You can import installed packages just as you would
    on your actual device:
        \b
        >>> # main.py
        >>> import <package_name>

    """
    project = mpy.project
    if not project.exists:
        mpy.log.error("You are not currently in an active project!")
        sys.exit(1)
    if path:
        pkg_name = next(iter(packages), None)
        mpy.log.title("Installing Local Package")
        pkg_path = "-e " + path
        project.add_package(pkg_path, dev=dev, name=pkg_name)
        sys.exit(0)
    if not packages:
        mpy.log.title("Installing all Requirements")
        try:
            project.add_from_file(dev=dev)
        except Exception as e:
            mpy.error(f"Failed to load requirements!", exception=e)
            raise click.Abort()
        else:
            mpy.log.success("\nRequirements Installed!")
            sys.exit(0)
    mpy.log.title("Installing Packages")
    for pkg in packages:
        try:
            project.add_package(pkg, dev=dev)
        except exc.RequirementException as e:
            pkg_name = str(e.package)
            mpy.log.error((f"Failed to install {pkg_name}!"
                           " Is it available on PyPi?"), exception=e)
            raise click.Abort()


@stubs.command(short_help="Add Stubs from package or path")
@click.argument('stub_name', required=True)
@click.option('-f', '--force', is_flag=True, default=False,
              help="Overwrite Stub if it exists.")
@pass_mpy
def add(mpy, stub_name, force=False):
    """Add Stubs from package or path.

    \b
    In general, stub package names follow this schema:
        <device>-<firmware>-<version>

    \b
    For example:
        esp32-micropython-1.11.0

    \b
    You can search premade stub packages using:
        micropy stubs search <QUERY>

    Checkout the docs on Github for more info.

    """
    mpy.stubs.verbose_log(True)
    proj = mpy.project
    mpy.log.title(f"Adding $[{stub_name}] to stubs")
    try:
        stub = mpy.stubs.add(stub_name, force=force)
    except exc.StubNotFound:
        mpy.log.error(f"$[{stub_name}] could not be found!")
        sys.exit(1)
    except exc.StubError:
        mpy.log.error(f"$[{stub_name}] is not a valid stub!")
        sys.exit(1)
    else:
        if proj.exists:
            mpy.log.title(f"Adding $[{stub.name}] to $[{proj.name}]")
            proj.add_stub(stub)


@stubs.command()
@click.argument('query', required=True)
@pass_mpy
def search(mpy, query):
    """Search available Stubs."""
    mpy.log.title(f"Searching Stub Repositories...")
    results = mpy.stubs.search_remote(query)
    mpy.log.title(f"Results for $[{query}]:")
    for pkg, installed in results:
        name = f"{pkg} $B[(Installed)]" if installed else pkg
        mpy.log.info(name)


@stubs.command()
@pass_mpy
def list(mpy):
    """List installed stubs."""
    def print_stubs(stub_list):
        for firm, stubs in stub_list:
            if stubs:
                title = str(firm).capitalize()
                mpy.log.title(f"$[{title}]:")
                for stub in stubs:
                    mpy.log.info(str(stub))
    mpy.log.title("Installed Stubs:")
    mpy.log.info(f"Total: {len(mpy.stubs)}")
    print_stubs(mpy.stubs.iter_by_firmware())
    mpy.verbose = False
    proj = mpy.project
    if proj.exists:
        mpy.log.title(f"Stubs used in {proj.name}:")
        mpy.log.info(f"Total: {len(proj.stubs)}")
        stubs = mpy.stubs.iter_by_firmware(stubs=proj.stubs)
        print_stubs(stubs)


@stubs.command(short_help="Create Stubs from Pyboard")
@click.argument('port', required=True)
@click.option('-v', '--verbose', is_flag=True, default=False,
              help="Enable verbose output")
@pass_mpy
def create(mpy, port, verbose=False):
    """Create stubs from a pyboard at <PORT>

    \b
    MicropyCli uses Josverl's micropython-stubber for stub creation.
    For more information, please visit the repository
    at: https://github.com/Josverl/micropython-stubber

    """
    if not utils.CREATE_STUBS_INSTALLED:
        mpy.log.error("\nMissing requirements!")
        mpy.log.info((
            "To create stubs, Micropy Cli depends on "
            "$[PyMinifier] and $[rshell]."
        ))
        mpy.log.info((
            "To install the extra requirements needed, "
            "please execute: $B[pip install micropy-cli[create_stubs]]"
        ))
        sys.exit(1)
    return mpy.create_stubs(port, verbose=verbose)


if __name__ == "__main__":
    cli()
