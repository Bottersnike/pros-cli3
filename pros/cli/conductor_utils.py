import glob
import os.path
import tempfile
import zipfile
from typing import *
from semantic_version import Spec, Version

import click

import pros.conductor as c
from pros.common.utils import logger
from pros.conductor.templates import ExternalTemplate
from .common import default_options
from .conductor import conductor


@conductor.command('create-template', context_settings={'allow_extra_args': True, 'ignore_unknown_options': True})
@click.argument('path', type=click.Path(exists=True))
@click.argument('name')
@click.argument('version')
@click.option('--install', 'install_files', multiple=True, type=click.Path())
@click.option('--user', 'user_files', multiple=True, type=click.Path())
@click.option('--kernels', 'supported_kernels')
@click.option('--target')
@click.option('--destination', type=click.Path())
@click.option('--zip/--no-zip', 'do_zip', default=True)
@default_options
@click.pass_context
def create_template(ctx, path: str, destination: str, do_zip: bool, **kwargs):
    project = c.Project.find_project(path)
    if project:
        project = c.Project(project)
        if not kwargs['supported_kernels']:
            kwargs['supported_kernels'] = f'^{project.kernel}'
        kwargs['target'] = project.target
    if not destination:
        if os.path.isdir(path):
            destination = path
        else:
            destination = os.path.dirname(path)
    kwargs['install_files'] = list(kwargs['install_files'])
    kwargs['user_files'] = list(kwargs['user_files'])
    kwargs['metadata'] = {ctx.args[i][2:]: ctx.args[i + 1] for i in range(0, len(ctx.args), 2)}

    def get_matching_files(globs: List[str]) -> Set[str]:
        matching_files: List[str] = []
        for g in globs:
            files = glob.glob(f'{path}/{g}', recursive=True)
            files = filter(lambda f: os.path.isfile(f), files)
            files = [os.path.normpath(f.split(f'{path}/')[-1]) for f in files]
            matching_files.extend(files)
        return set(matching_files)

    matching_install_files: Set[str] = get_matching_files(kwargs['install_files'])
    matching_user_files: Set[str] = get_matching_files(kwargs['user_files'])

    matching_install_files: Set[str] = matching_install_files - matching_user_files

    if project:
        project_template_files = set(project.list_template_files())
        matching_install_files = matching_install_files - project_template_files
        matching_user_files = matching_user_files - project_template_files

    kwargs['install_files'] = list(matching_install_files)
    kwargs['user_files'] = list(matching_user_files)

    if do_zip:
        if not os.path.isdir(destination) and os.path.splitext(destination)[-1] != '.zip':
            logger(__name__).error(f'{destination} must be a zip file or an existing directory.')
            return -1
        with tempfile.TemporaryDirectory() as td:
            template = ExternalTemplate(file=os.path.join(td, 'template.pros'), **kwargs)
            template.save()
            if os.path.isdir(destination):
                destination = os.path.join(destination, f'{template.identifier}.zip')
            with zipfile.ZipFile(destination, mode='w') as z:
                z.write(template.save_file, arcname='template.pros')

                for file in kwargs['user_files']:
                    print(f'Adding {file}')
                    z.write(f'{path}/{file}', file)
                for file in kwargs['install_files']:
                    print(f'Adding {file}')
                    z.write(f'{path}/{file}', file)
    else:
        if os.path.isdir(destination):
            destination = os.path.join(destination, 'template.pros')
        template = ExternalTemplate(file=destination, **kwargs)
        template.save()
