#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""MicropyCli Console Entrypoint"""
import click

from micropy.main import MicroPy
from micropy.project import Project

mp = MicroPy()


@click.group()
def cli():
    pass


@cli.group()
def stubs():
    """Manage Stubs"""


@cli.command()
@click.argument('project_name', required=True)
def init(project_name=""):
    """Create new Micropython Project"""
    mp.log.info("Creating New Project...")
    project = Project(project_name)
    project.create()


@cli.command()
@click.argument('project_name', required=True)
def reload(project_name=''):
    """Reload Stubs"""
    project = Project(project_name)
    project.refresh_stubs()


@stubs.command()
@click.argument('path', required=True, type=click.Path(exists=True, file_okay=False, resolve_path=True))
def add(path):
    """Add stubs"""
    return mp.add_stub(path)


@stubs.command()
def list():
    """Lists all stubs"""
    return mp.list_stubs()


@stubs.command()
@click.argument('port', required=True)
def create(port):
    """Create stubs from a pyboard"""
    return mp.create_stubs(port)


if __name__ == "__main__":
    cli()
