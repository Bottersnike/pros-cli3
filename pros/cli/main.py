import logging

import click

import pros.cli.build
import pros.cli.conductor
import pros.cli.conductor_utils
import pros.cli.terminal
import pros.cli.upload
import pros.cli.v5_utils
import pros.cli.test
import pros.common.ui as ui
from pros.common.utils import get_version, logger
from .click_classes import *
from .common import default_options


def main():
    try:
        ctx_obj = {}
        pros_logger = logging.getLogger(pros.__name__)
        pros_logger.propagate = False
        click_handler = ui.PROSLogHandler(ctx_obj=ctx_obj)
        # click_handler = logging.StreamHandler()
        click_handler.setLevel(logging.WARNING)
        ctx_obj['click_handler'] = click_handler
        formatter = ui.PROSLogFormatter('%(levelname)s - %(name)s:%(funcName)s - %(message)s', ctx_obj)
        click_handler.setFormatter(formatter)
        pros_logger.addHandler(click_handler)
        pros_logger.setLevel(logging.WARNING)

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
               sources=[pros.cli.build.build_cli,
                        pros.cli.terminal.terminal_cli,
                        pros.cli.upload.upload_cli,
                        pros.cli.v5_utils.v5_utils_cli,
                        pros.cli.conductor.conductor_cli,
                        pros.cli.test.test_cli])
@default_options
@click.option('--version', help='Displays version and exits', is_flag=True, expose_value=False, is_eager=True,
              callback=version)
def cli():
    pass


if __name__ == '__main__':
    main()
