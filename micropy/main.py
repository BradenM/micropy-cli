#!/usr/bin/env python
# -*- coding: utf-8 -*-


import click
from pathlib import Path
from micropy.project import Project
from micropy.micropy import MicroPy
import requests

mp = MicroPy()

@click.group()
def cli():
    pass

@cli.group()
def stubs():
    """Manage Stubs"""
    pass


@cli.command()
@click.argument('project_name', required=True)
def init(project_name=""):
    """Create new Micropython Project"""
    mp.log.info("Creating New Project...")
    project = Project(project_name)
    project.setup()
    project.create()

@cli.command()
@click.argument('project_name', required=True)
def reload(project_name=''):
    """Reload Stubs"""
    project = Project(project_name)
    project.refresh_stubs()

@stubs.command()
def get():
    """Retrieves createstubs.py"""
    CREATE_STUB = "https://raw.githubusercontent.com/Josverl/micropython-stubber/master/createstubs.py"
    out = Path.cwd() / 'createstubs.py'
    mp.log.info("Retrieving $[createstubs.py] from $[Josverl/micropython-stubber]...")
    content = requests.get(CREATE_STUB)
    out.write_text(content.text)
    mp.log.info(f"Request complete, outputted to: {out.resolve()}")
    mp.log.success("Done!")

@stubs.command()
@click.argument('path', required=True, type=click.Path(exists=True, file_okay=False, resolve_path=True))
def add(path):
    """Add stubs"""
    project = Project("Stubs")
    project.add_stub(path)



if __name__ == "__main__":
    cli()
