import os.path
from typing import *

import semantic_version as semver

from pros.common.utils import get_pros_dir
from pros.config.config import Config


class Template(Config):
    def __init__(self, file):
        self.name = None  # type: str
        self.version = None  # type: str
        self.supported_kernels = None  # type: str
        self.library_dependencies = {}  # type: set
        self.install_files = []  # type: List[str]
        self.template_ignore = ['template.pros']  # type: List[str]
        self.remove_paths = []  # type: List[str]
        self.origin = None  # type: str
        super(Template, self).__init__(file)
        if 'template.pros' not in self.template_ignore:
            self.template_ignore.append('template.pros')

    @property
    def identifier(self):
        return TemplateIdentifier(self.name, self.version)


class TemplateIdentifier(object):
    def __init__(self, *args: str):
        if len(args) == 1:
            arg = args[0]
            if arg.count('@') != 1:
                raise ValueError('{} should be a valid template identifier string'.format(arg))
            self.name, self.version = args[0].split('@', 1)
        elif len(args) == 2:
            self.name = args[0]
            self.version = args[1]

        if not semver.validate(self.version):
            raise ValueError('{} is not a valid semantic version string'.format(self.version))

    def __str__(self):
        return '{}@{}'.format(self.name, self.version)

    def __getstate__(self):
        return {
            'name': self.name,
            'version': self.version
        }

    @property
    def installed_location(self):
        return os.path.join(get_pros_dir(), 'templ', str(self))

    @property
    def installed_config_file(self):
        return os.path.join(self.installed_location, 'template.pros')

    @property
    def installed_config(self):
        return Template(self.installed_config_file)


class TemplateSpecifier(TemplateIdentifier):
    def __init__(self, *args: str):
        if len(args) == 1:
            arg = args[0]
            if arg.count('@') != 1:
                raise ValueError('{} should be a valid template identifier string'.format(arg))
            self.name, self.version = args[0].split('@', 1)
        elif len(args) == 2:
            self.name = args[0]
            self.version = args[1]
        else:
            raise ValueError('Arguments may contain up to 2 items (got {})'.format(len(args)))

        try:
            self.version = semver.Spec(self.version)
        except ValueError:
            raise ValueError('{} is not a valid semantic version specifier'.format(self.version))
