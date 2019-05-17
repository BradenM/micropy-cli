#!/usr/bin/env python
# -*- coding: utf-8 -*-


import click
from pathlib import Path
from micropy.project import Project


@click.group()
def cli():
    pass


@cli.command()
@click.argument('project_name', required=True)
def init(project_name=""):
    """Create new Micropython Project"""
    x = Project(project_name)


if __name__ == "__main__":
    cli()
