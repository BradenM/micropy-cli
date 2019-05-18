#!/usr/bin/env python
# -*- coding: utf-8 -*-


import click
from pathlib import Path
from micropy.project import Project
from micropy.logger import ServiceLog

log = ServiceLog('MicroPy', 'bright_blue', root=True)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('project_name', required=True)
def init(project_name=""):
    """Create new Micropython Project"""
    log.info("Creating New Project...")
    project = Project(project_name)


if __name__ == "__main__":
    cli()
