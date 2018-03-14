import pros.common.ui as ui
from .click_classes import *
from .common import default_options


@click.group(cls=PROSGroup)
def test_cli():
    pass


@test_cli.command()
@default_options
def test():
    ui.echo('Hello World!')
    with ui.Notification():
        ui.echo('Hello from another box')
