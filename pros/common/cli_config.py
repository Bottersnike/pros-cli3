import os.path
from typing import *

import click

from pros.conductor.templates.template import Template
# import pros.conductor.providers.github_releases as githubreleases
from pros.config.config import Config


class CliConfig(Config):
    def __init__(self, file=None):
        if not file:
            file = os.path.join(click.get_app_dir('PROS'), 'cli.pros')
        self.default_libraries = []  # type: List[str]
        self.providers = []  # type: List[str]
        self.templates = []  # type: List[Template]

        super(CliConfig, self).__init__(file)

    def reset_providers(self):
        pass
        # if os.path.isfile(githubreleases.__file__):
        #     self.providers = [githubreleases.__file__]
        # elif hasattr(sys, 'frozen'):
        #     self.providers = [os.path.join(os.path.dirname(sys.executable), 'githubreleases.pyc')]


def cli_config() -> CliConfig:
    ctx = click.get_current_context(silent=True)
    ctx.ensure_object(dict)
    assert isinstance(ctx.obj, dict)
    if not hasattr(ctx.obj, 'cli_config') or not isinstance(ctx.obj['cli_config'], CliConfig):
        ctx.obj['cli_config'] = CliConfig()
    return ctx.obj['cli_config']
