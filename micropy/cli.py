#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""MicropyCli Console Entrypoint"""
import sys

import click
import questionary as prompt
from questionary import Choice

import micropy.exceptions as exc
from micropy.main import MicroPy
from micropy.project import Project


@click.group()
@click.version_option()
def cli():
    """CLI Application for creating/managing Micropython Projects."""


@cli.group(short_help="Manage Micropy Stubs")
def stubs():
    """Manage Micropy Stubs

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
@click.argument('project_name', required=True)
def init(project_name=""):
    """Create new Micropython Project

    \b
    When creating a new project, all files will be
    placed under the generated <PROJECT_NAME> folder.
    """
    mp = MicroPy()
    mp.log.title("Creating New Project...")
    stubs = [Choice(str(s), value=s) for s in mp.STUBS]
    if not stubs:
        mp.log.error("You don't have any stubs!")
        mp.log.title(
            "To add stubs to micropy, use $[micropy stubs add <STUB_NAME>]")
        sys.exit(1)
    stub_choices = prompt.checkbox(
        "Which stubs would you like to use?", choices=stubs).ask()
    project = Project(project_name, stub_choices)
    proj_relative = project.create()
    mp.log.title(f"Created $w[{project.name}] at $w[./{proj_relative}]")


@stubs.command(short_help="Add Stubs from package or path")
@click.argument('stub_name', required=True)
def add(stub_name):
    """Add Stubs from package or path

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
    mp = MicroPy()
    mp.STUBS.verbose_log(True)
    mp.log.title(f"Adding $[{stub_name}] to stubs...")
    try:
        stub = mp.STUBS.add(stub_name)
    except exc.StubNotFound:
        mp.log.error(f"$[{stub_name}] could not be found!")
        sys.exit(1)
    except exc.StubError:
        mp.log.error(f"$[{stub_name}] is not a valid stub!")
        sys.exit(1)
    else:
        mp.log.success(f"{str(stub)} added!")


@stubs.command()
@click.argument('query', required=True)
def search(query):
    """Search available Stubs"""
    mp = MicroPy()
    mp.log.title(f"Searching Stub Repositories...")
    results = mp.STUBS.search_remote(query)
    mp.log.title(f"Results for $[{query}]:")
    for pkg, installed in results:
        name = f"{pkg} $B[(Installed)]" if installed else pkg
        mp.log.info(name)


@stubs.command()
def list():
    """List installed stubs"""
    mp = MicroPy()
    mp.log.title("Installed Stubs:")
    for stub in mp.STUBS:
        mp.log.info(str(stub))
    return mp.log.info(f"$[Total:] {len(mp.STUBS)}")


@stubs.command(short_help="Create Stubs from Pyboard")
@click.argument('port', required=True)
def create(port):
    """Create stubs from a pyboard at <PORT>

    \b
    MicropyCli uses Josverl's micropython-stubber for stub creation.
    For more information, please visit the repository
    at: https://github.com/Josverl/micropython-stubber
    """
    mp = MicroPy()
    return mp.create_stubs(port)


if __name__ == "__main__":
    cli()
