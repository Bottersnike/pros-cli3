import logging
import os.path

import click

import pros.common.ui as ui
from pros.cli.click_classes import *
from pros.cli.common import default_options, root_commands
from pros.common.utils import get_version, logger

root_sources = [
    'build',
    'conductor',
    'conductor_utils',
    'misc_commands',
    'terminal',
    'upload',
    'v5_utils'
]

if os.path.exists(os.path.join(__file__, '..', '..', '..', '.git')):
    root_sources.append('test')

for root_source in root_sources:
    __import__(f'pros.cli.{root_source}')


def main():
    try:
        ctx_obj = {}
        click_handler = ui.PROSLogHandler(ctx_obj=ctx_obj)
        ctx_obj['click_handler'] = click_handler
        formatter = ui.PROSLogFormatter('%(levelname)s - %(name)s:%(funcName)s - %(message)s', ctx_obj)
        click_handler.setFormatter(formatter)
        logging.basicConfig(level=logging.WARNING, handlers=[click_handler])

        cli.main(prog_name='pros', obj=ctx_obj)
    except KeyboardInterrupt:
        click.echo('Aborted!')
    except Exception as e:
        logger(__name__).exception(e)


def version(ctx: click.Context, param, value):
    if not value:
        return
    ctx.ensure_object(dict)
    if ctx.obj.get('machine_output', False):
        click.echo(get_version())
    else:
        click.echo('pros, version {}'.format(get_version()))
    ctx.exit(0)


@click.command('pros',
               cls=PROSCommandCollection,
               sources=root_commands)
@default_options
@click.option('--version', help='Displays version and exits', is_flag=True, expose_value=False, is_eager=True,
              callback=version)
def cli():
    pass


if __name__ == '__main__':
    main()
