import os.path
import shutil

from pros.conductor import BaseTemplate, Template
from pros.conductor.templates import ExternalTemplate
from pros.config.config import ConfigNotFoundException
from .depot import Depot


class LocalDepot(Depot):
    def fetch_template(self, template: BaseTemplate, destination: str, **kwargs) -> Template:
        if 'location' not in kwargs:
            raise KeyError('Location of local template must be specified.')
        if os.path.isdir(kwargs['location']):
            location_dir = kwargs['location']
            if not os.path.isfile(os.path.join(location_dir, 'template.pros')):
                raise ConfigNotFoundException(f'A template.pros file was not found in {location_dir}.')
            template_file = os.path.join(location_dir, 'template.pros')
        elif os.path.isfile(kwargs['location']):
            location_dir = os.path.dirname(kwargs['location'])
            template_file = kwargs['location']
        else:
            raise ValueError(f"The specified location was not a file or directory ({kwargs['location']}).")
        shutil.copytree(location_dir, destination)
        return ExternalTemplate(file=template_file)

    def __init__(self):
        super().__init__('local', 'local')
