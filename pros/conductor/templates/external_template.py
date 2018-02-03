import os.path

from pros.config import Config
from .template import Template


class ExternalTemplate(Config, Template):
    def __init__(self, file: str, **kwargs):
        if os.path.isdir(file):
            file = os.path.join(file, 'template.pros')
        Template.__init__(self, **kwargs)
        Config.__init__(self, file)
