#!/usr/bin/env python3

import click
from pathlib import Path
from project import Project


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
