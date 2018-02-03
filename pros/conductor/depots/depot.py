from typing import *

from pros.conductor import BaseTemplate, Template


class Depot(object):
    def __init__(self, name: str, location: str, config: Dict[str, Any] = None,
                 config_schema: Dict[str, Dict[str, Any]] = None):
        self.name: str = name
        self.location: str = location
        self.config: Dict[str, Any] = config or {}
        self.config_schema: Dict[str, Dict[str, Any]] = config_schema or {}
        self.remote_templates: List[BaseTemplate] = []

    def update_remote_templates(self):
        pass

    def fetch_template(self, template: BaseTemplate, destination: str, **kwargs) -> Template:
        raise NotImplementedError()
