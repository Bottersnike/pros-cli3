from typing import *

from .base_template import BaseTemplate


class Template(BaseTemplate):
    def __init__(self, **kwargs):
        self.install_files: List[str] = []
        self.user_files: List[str] = []
        super().__init__(**kwargs)
