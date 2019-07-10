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


@cli.group()
def stubs():
    """Manage Stubs"""


@cli.command()
@click.argument('project_name', required=True)
def init(project_name=""):
    """Create new Micropython Project"""
    mp = MicroPy()
    mp.log.info("Creating New Project...")
    stubs = [Choice(str(s), value=s) for s in mp.STUBS]
    stub_choices = prompt.checkbox(
        "Which stubs would you like to use?", choices=stubs).ask()
    project = Project(project_name, stub_choices)
    proj_relative = project.create()
    mp.log.info(f"Created $[{project.name}] at $w[./{proj_relative}]")


@stubs.command()
@click.argument('stub_name', required=True)
def add(stub_name):
    """Add Stubs from package or path"""
    mp = MicroPy()
    mp.STUBS.verbose_log(True)
    mp.log.info(f"Adding $[{stub_name}] to stubs...")
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
def list():
    """Lists available stubs"""
    mp = MicroPy()
    mp.log.info("$w[Available Stubs:]")
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
