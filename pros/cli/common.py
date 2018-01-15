import click.core

from pros.common.utils import *


def logging_option(f):
    def callback(ctx: click.Context, param: click.core.Parameter, value: Any):
        if value is None:
            return None
        ctx.ensure_object(dict)
        if isinstance(value, str):
            value = getattr(logging, value.upper(), None)
        if not isinstance(value, int):
            raise ValueError('Invalid log level: {}'.format(value))
        logger().setLevel(value)
        stdout_handler = ctx.obj['click_handler']  # type: logging.Handler
        stdout_handler.setLevel(value)
        return value

    return click.option('-l', '--log', help='Logging level', is_eager=True, expose_value=False, callback=callback,
                        type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']))(f)


def logfile_option(f):
    def callback(ctx: click.Context, param: click.core.Parameter, value: Any):
        if value is None or value[0] is None:
            return None
        ctx.ensure_object(dict)
        level = None
        if isinstance(value[1], str):
            level = getattr(logging, value[1].upper(), None)
        if not isinstance(level, int):
            raise ValueError('Invalid log level: {}'.format(value[1]))
        handler = logging.StreamHandler(value[0])
        fmt_str = '%(name)s.%(funcName)s:%(levelname)s - %(asctime)s - %(message)s'
        handler.setFormatter(logging.Formatter(fmt_str))
        handler.setLevel(level)
        logger().addHandler(handler)
        logger().setLevel(min(logger().level, level))

    return click.option('--logfile', help='Log messages to a file', is_eager=True, expose_value=False,
                        callback=callback, default=(None, None),
                        type=click.Tuple(
                            [click.File('a'), click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])]
                        ))(f)


def verbosity_option(f):
    """
    provides a wrapper for creating the verbosity option (so don't have to create callback, parameters, etc.)
    """

    def callback(ctx: click.Context, param: click.core.Parameter, value: Any):
        ctx.ensure_object(dict)
        ctx.obj[param.name] = value
        logging.basicConfig(level=logging.INFO)
        return value

    return click.option('-v', '--verbose', count=True, expose_value=False, help='Sets log level to INFO',
                        is_eager=True, callback=callback)(f)


def machine_output_option(f):
    """
    provides a wrapper for creating the machine output option (so don't have to create callback, parameters, etc.)
    """

    def callback(ctx, param, value):
        ctx.ensure_object(dict)
        ctx.obj[param.name] = value
        return value

    decorator = click.option('--machine-output', expose_value=False, is_flag=True, default=False, is_eager=True,
                             help='Enable machine friendly output.', callback=callback)(f)
    decorator.__name__ = f.__name__
    return decorator


def default_options(f):
    """
     combines verbosity, debug, machine output options (most commonly used)
    """
    decorator = verbosity_option(logging_option(logfile_option(machine_output_option(f))))
    decorator.__name__ = f.__name__
    return decorator


class AliasGroup(click.Group):
    def __init__(self, *args, **kwargs):
        super(AliasGroup, self).__init__(*args, **kwargs)
        self.cmd_dict = dict()

    def command(self, *args, aliases=None, **kwargs):
        aliases = aliases or []

        def decorator(f):
            for alias in aliases:
                self.cmd_dict[alias] = f.__name__ if len(args) == 0 else args[0]
            cmd = super(AliasGroup, self).command(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd

        return decorator

    def group(self, aliases=None, *args, **kwargs):
        aliases = aliases or []

        def decorator(f):
            for alias in aliases:
                self.cmd_dict[alias] = f.__name__
            cmd = super(AliasGroup, self).group(*args, **kwargs)(f)
            self.add_command(cmd)
            return cmd

        return decorator

    def get_command(self, ctx, cmd_name):
        # return super(AliasGroup, self).get_command(ctx, cmd_name)
        suggestion = super(AliasGroup, self).get_command(ctx, cmd_name)
        if suggestion is not None:
            return suggestion
        if cmd_name in self.cmd_dict:
            return super(AliasGroup, self).get_command(ctx, self.cmd_dict[cmd_name])

        # fall back to guessing
        matches = {x for x in self.list_commands(ctx) if x.startswith(cmd_name)}
        matches.union({x for x in self.cmd_dict.keys() if x.startswith(cmd_name)})
        if len(matches) == 1:
            return super(AliasGroup, self).get_command(ctx, matches.pop())
        return None
