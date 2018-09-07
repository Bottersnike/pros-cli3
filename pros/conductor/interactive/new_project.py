from typing import *

import pros.common.ui.interactive as iui
from ..conductor import Conductor

from semantic_version import Version


class NewProjectPrompt(object):
    def __init__(self, conductor: Conductor):
        self.conductor = conductor
        self.prompt = iui.InteractivePrompt('Create a Project', confirm='Create Project')
        self.selections = {}

    def get_elements(self) -> Generator[iui.Element, None, None]:
        yield iui.FolderSelector('project_path', self.get('project_path', ''))
        yield iui.TextInput('project_name', self.get('project_name', ''))
        platform = self.get('platform', self.conductor.default_target).lower()
        yield iui.DropdownSelector('platform', platform.title(), ['V5', 'Cortex'], title='Platform')
        kernel = self.get('templates:kernel', 'latest')
        templates = [
            iui.DropdownSelector('kernel', kernel,
                                 ['latest'] +
                                 sorted([
                                     t.version
                                     for t
                                     in self.conductor.resolve_templates('kernel', target=platform, unique=True)
                                 ], key=lambda v: Version(v), reverse=True)
                                 )
        ]
        templates += [
            iui.DropdownSelector(default_template, self.get(f'templates:{default_template}', 'latest'),
                                 ['latest', 'not installed'] +
                                 sorted([
                                     t.version
                                     for t
                                     in self.conductor.resolve_templates(default_template, target=platform,
                                                                         kernel_version=kernel if kernel != 'latest' else '',
                                                                         unique=True)
                                 ], key=lambda v: Version(v), reverse=True))
            for default_template
            in self.conductor.default_libraries[platform]
        ]
        yield iui.GroupElement('templates', templates)

    @property
    def valid(self):
        return bool(self.selections.get('project_path', ''))

    def get(self, value, default=None):
        r = self.selections
        for v in value.split(':'):
            if v not in r:
                return default
            r = r[v]
        return r

    def execute(self):
        done = False
        while not done or not self.valid:
            done, results = self.prompt(list(self.get_elements()), self.valid)
            self.selections = results
