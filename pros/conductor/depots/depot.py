from typing import *
from datetime import datetime, timedelta

from pros.conductor import BaseTemplate, Template


class Depot(object):
    def __init__(self, name: str, location: str, config: Dict[str, Any] = None,
                 config_schema: Dict[str, Dict[str, Any]] = None):
        self.name: str = name
        self.location: str = location
        self.config: Dict[str, Any] = config or {}
        self.config_schema: Dict[str, Dict[str, Any]] = config_schema or {}
        self.remote_templates: List[BaseTemplate] = []
        self.last_remote_update: datetime = datetime.now()

    def update_remote_templates(self):
        pass

    def fetch_template(self, template: BaseTemplate, destination: str, **kwargs) -> Template:
        raise NotImplementedError()

    def get_remote_templates(self, auto_check_freq: Optional[timedelta]=None, force_check: bool=False):
        if auto_check_freq is None:
            auto_check_freq = timedelta(weeks=1)
        if force_check or datetime.now() - self.last_remote_update > auto_check_freq:
            self.update_remote_templates()
        for t in self.remote_templates:
            t.metadata['origin'] = self.name
        return self.remote_templates
