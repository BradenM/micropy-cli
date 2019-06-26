#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""MicropyCli Console Entrypoint"""
import sys
from pathlib import Path

import click
import questionary as prompt
from questionary import Choice

from micropy.exceptions import StubError
from micropy.main import MicroPy
from micropy.project import Project

mp = MicroPy()


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
    mp.log.info("Creating New Project...")
    stubs = [Choice(str(s), value=s) for s in mp.STUBS]
    stub_choices = prompt.checkbox(
        "Which stubs would you like to use?", choices=stubs).ask()
    project = Project(project_name, stub_choices)
    proj_relative = project.create()
    mp.log.info(f"Created $[{project.name}] at $w[./{proj_relative}]")


@stubs.command()
@click.argument('path', required=True, type=click.Path(
    exists=True, file_okay=False, resolve_path=True))
def add(path):
    """Add stubs"""
    stub_path = Path(str(path))
    try:
        mp.log.info(f"Adding stub from $[{stub_path}]")
        mp.STUBS.validate(stub_path)
        stub = mp.STUBS.add(stub_path)
    except StubError:
        msg = f"{stub_path.name} is not a valid stub!"
        mp.log.error(msg)
        sys.exit(1)
    else:
        mp.log.success(f"{stub.name} added!")


@stubs.command()
def list():
    """Lists available stubs"""
    mp.log.info("$w[Available Stubs:]")
    for stub in mp.STUBS:
        mp.log.info(str(stub))
    return mp.log.info(f"$[Total:] {len(mp.STUBS)}")


@stubs.command()
@click.argument('port', required=True)
def create(port):
    """Create stubs from a pyboard

    MicropyCli uses Josverl's micropython-stubber for stub creation.
    For more info,
    checkout his git repo @ https://github.com/Josverl/micropython-stubber
    """
    return mp.create_stubs(port)


if __name__ == "__main__":
    cli()
