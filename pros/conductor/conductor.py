import os.path
import shutil
from typing import *

import click

from pros.common.utils import logger
from pros.conductor.depots.depot import Depot
from pros.config import Config
from .templates import LocalTemplate, BaseTemplate, Template


class Conductor(Config):
    def __init__(self, file=None):
        if not file:
            file = os.path.join(click.get_app_dir('PROS'), 'conductor.pros')
        self.local_templates: Set[LocalTemplate] = set()
        self.depots: List[Depot] = []
        super(Conductor, self).__init__(file)

    def fetch_template(self, depot: Depot, template: BaseTemplate, **kwargs):
        if 'destination' in kwargs:
            destination = kwargs.pop('destination')
        else:
            destination = os.path.join(self.directory, 'templates', template.identifier)
            if os.path.isdir(destination):
                shutil.rmtree(destination)

        for t in self.local_templates:
            if hash(t) == template:
                self.remove_template(t)

        template: Template = depot.fetch_template(template, destination, **kwargs)
        local_template = LocalTemplate(orig=template, location=destination)
        self.local_templates.add(local_template)
        self.save()

    def remove_template(self, template: LocalTemplate):
        if template not in self.local_templates:
            logger(__name__).debug(f"{template.identifier} was not in the Conductor's local templates cache.")
        else:
            self.local_templates.remove(template)

        if os.path.abspath(template.location).startswith(
                os.path.abspath(os.path.join(self.directory, 'templates'))) \
                and os.path.isdir(template.location):
            shutil.rmtree(template.location)
