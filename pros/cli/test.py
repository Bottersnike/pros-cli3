import pros.common.ui as ui
from .click_classes import *
from .common import default_options

from pros.common import logger

import time


@click.group(cls=PROSGroup)
def test_cli():
    pass


@test_cli.command()
@default_options
def test():
    ui.echo('Hello World!')
    with ui.Notification():
        ui.echo('Hello from another box')
    ui.echo('Back on the other one', nl=False)
    ui.echo('Whoops I missed a newline')
    with ui.Notification():
        ui.echo('Yet another box')
        with ui.progressbar(range(20)) as bar:
            for _ in bar:
                time.sleep(0.25)
    ui.echo('Back again bitches')

    logger(__name__).warning('Hello')
    try:
        raise Exception('Hey')
    except Exception as e:
        logger(__name__).exception(e)


