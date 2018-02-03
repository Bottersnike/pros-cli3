import os.path
from typing import *

import click

import pros.common
import pros.conductor as c
from pros.conductor.templates import ExternalTemplate
from pros.cli.common import default_options
from pros.cli.click_classes import PROSGroup
from pros.common.utils import logger


@click.group(cls=PROSGroup)
def conductor_cli():
    pass


@conductor_cli.group(cls=PROSGroup, aliases=['cond', 'c', 'conduct'], short_help='Perform project management for PROS')
@default_options
def conductor():
    pass


@conductor.command(aliases=['download'], short_help='Fetch/Download a remote template',
                   context_settings={'allow_extra_args': True, 'ignore_unknown_options': True})
@click.argument('spec')
@click.option('--depot', default=None)
@click.option('--destination', type=click.Path(file_okay=False))
@default_options
@click.pass_context
def fetch(ctx, spec, depot, destination):
    extra_args = {ctx.args[i][2:]: ctx.args[i + 1] for i in range(0, len(ctx.args), 2)}
    if depot == 'local':
        if 'location' not in extra_args:
            logger(__name__).error('Location must be specified when using local depot.')
            return -1
        template = ExternalTemplate(file=extra_args['location']) # blank template since we don't care
        print(template.identifier)
        depot = c.LocalDepot()
    else:
        # TODO: implement selecting a template
        template = None
        depot = None
    c.Conductor().fetch_template(depot, template, **extra_args)


@conductor.command()
@click.option('--upgrade/--no-upgrade', 'upgrade_ok', default=True)
@click.option('--install/--no-install', 'install_ok', default=True)
@click.option('--download/--no-download', 'download_ok', default=True)
@click.option('--upgrade-user-files/--no-upgrade-user-files', 'upgrade_user_files', default=False)
@click.argument('path', default='.', type=click.Path())
@click.argument('templates', nargs=-1)
@default_options
def apply(upgrade_ok: bool, install_ok: bool, download_ok: bool, path: str, templates: List[str],
          upgrade_user_files: bool=False):
    project_path = c.Project.find_project(path)
    if project_path is None:
        pros.common.logger(__name__).error('{} is not inside a PROS project'.format(path))
        return -1
    project = c.Project(project_path)


@conductor.command(aliases=['i', 'in'])
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
    project.kernel = version
    project.target = platform
    project.save()
    click.echo('Created a new project at {} for {}'.format(os.path.abspath(project.location), project.target))


@conductor.command('info-project')
@click.argument('path', type=click.Path(exists=True), default='.', required=False)
@default_options
def info_project(path: str):
    project_path = c.Project.find_project(path)
    if project_path is None:
        pros.common.logger(__name__).error('No project was found')
        return -1
    project = c.Project(path=project_path)
    click.echo(project.__getstate__())

