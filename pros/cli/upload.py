import serial.tools.list_ports as list_ports

import pros.conductor as c
from pros.serial.ports import SerialPort
from pros.serial.vex import *
from .click_classes import *
from .common import *


@click.group(cls=PROSGroup)
def upload_cli():
    pass


@upload_cli.command()
@click.option('--target', type=click.Choice(['v5', 'cortex']), default=None, required=False)
@click.argument('file', type=click.Path(exists=True), default=None, required=False)
@click.argument('port', type=str, default=None, required=False)
@click.option('--name', type=str, default=None, required=False)
@click.option('--slot', default=1, type=int)
@default_options
def upload(target: str, file: str, port: str, name: str = None, slot: int = 1):
    if file is None or os.path.isdir(file):
        project_path = c.Project.find_project(file or os.getcwd())
        if project_path is None:
            logger(__name__).error('Specify a file to upload or set the cwd inside a PROS project')
            return -1
        project = c.Project(project_path)
        file = project.output
        if name is None:
            name = project.name
        target = project.target
    if name is None:
        name = os.path.basename(file)
    if target is None:
        raise click.UsageError('Target not specified. specify a project (using the file argument) or target manually')
    if port is None:
        ports = []
        if target == 'v5':
            ports = find_v5_ports('system')
        elif target == 'cortex':
            ports = find_cortex_ports()
        if len(ports) == 0:
            logger(__name__).error('No {} ports were found! If you think you have a V5 plugged in, '
                                   'run this command again with the --debug flag'.format(target))
            if isdebug():
                logger(__name__).debug(','.join([x.__dict__ for x in list_ports.comports()]))
            return -1
        if len(ports) > 1:
            port = click.prompt('Multiple {} ports were found. Please choose one: '.format(target), default=port[0].device,
                                type=click.Choice([p.device for p in ports]))
            assert port in ports
        else:
            port = ports[0].device
            logger(__name__).info('Automatically selected {}'.format(port))
    click.echo('Uploading {} to {} device on {}'.format(file, target, port))
    if target == 'v5':
        click.echo('V5 program name: {}'.format(name))
    if not os.path.isfile(file) and file is not '-':
        logger(__name__).error('{} is not a valid file! Make sure it exists (e.g. by building your project)'.format(file))
        return -1
    try:
        ser = SerialPort(port)
        v5 = V5Device(ser)
        if name is None:
            name = os.path.splitext(os.path.basename(file))[0]
        with click.open_file(file, mode='rb') as pf:
            v5.write_program(pf, name, slot=slot - 1, run_after=True)
    except Exception as e:
        logger(__name__).debug(e, exc_info=True)
        click.echo(e, err=True)
        exit(1)
