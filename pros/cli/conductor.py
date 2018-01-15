import os.path
from typing import *

import click

import pros.common
import pros.conductor as c
from pros.cli.common import AliasGroup, default_options


@click.group(cls=AliasGroup)
def conductor_cli():
    pass


@conductor_cli.group(cls=AliasGroup, aliases=['cond', 'c', 'conduct'],  short_help='Perform project management for PROS')
def conductor():
    pass


@conductor.command()
@click.argument('name')
@click.argument('version', default='latest')
@default_options
def download(name, version):
    pass


@conductor.command()
@click.option('--upgrade/--no-upgrade', 'upgrade_ok', default=True)
@click.option('--install/--no-install', 'install_ok', default=True)
@click.option('--download/--no-download', 'download_ok', default=True)
@click.argument('project', default='.', type=click.Path())
@click.argument('templates', nargs=-1)
@default_options
def apply(upgrade_ok: bool, install_ok: bool, download_ok: bool, project: str, templates: List[str]):
    print(upgrade_ok, install_ok, download_ok, project, templates)
    pass


@conductor.command()
@click.option('--upgrade/--no-upgrade', 'upgrade_ok', default=False)
@click.option('--download/--no-download', 'download_ok', default=True)
@click.argument('project', default='.', type=click.Path())
@click.argument('templates', nargs=-1)
@default_options
@click.pass_context
def install(ctx: click.Context, **kwargs):
    ctx.invoke(apply, install_ok=True, **kwargs)


@conductor.command()
@click.option('--install/--no-install', 'install_ok', default=False)
@click.option('--download/--no-download', 'download_ok', default=True)
@click.argument('project', default='.', type=click.Path())
@click.argument('templates', nargs=-1)
@default_options
@click.pass_context
def upgrade(ctx: click.Context, **kwargs):
    ctx.invoke(apply, upgrade_ok=True, **kwargs)


@conductor.command(aliases=['new-project'])
@click.argument('path', type=click.Path())
@click.argument('platform', default='v5')
@click.argument('version', default='latest')
@default_options
def new(path: str, platform: str, version: str):
    if c.Project.find_project(path) is not None:
        pros.common.logger(__name__).error('A project already exists in this location! Delete it first')
        return -1
    project = c.Project(path=path, create=True, defaults={'platform': platform, 'version': version})
    project.kernel_version = version
    project.platform = platform
    project.save()
    click.echo('Created a new project at {} for {}'.format(os.path.abspath(project.location), project.platform))


