from typing import *

from semantic_version import Version, Spec


class BaseTemplate(object):
    def __init__(self, **kwargs):
        self.name: str = None
        self.version: str = None
        self.supported_kernels: str = None
        self.target: str = None
        self.metadata: Dict[str, Any] = {}
        if 'orig' in kwargs:
            self.__dict__.update({k: v for k, v in kwargs['orig'].__dict__.items() if k in self.__dict__})
        self.__dict__.update({k: v for k, v in kwargs.items() if k in self.__dict__})

    def satisfies(self, query: 'BaseTemplate') -> bool:
        if query.name and self.name != query.name:
            return False
        if query.target and self.target != query.target:
            return False
        if query.version and Version(self.version) not in Spec(query.version):
            return False
        if query.supported_kernels and \
                Version(query.supported_kernels) not in Spec(self.supported_kernels):
            return False
        keys_intersection = set().intersection(self.metadata.keys(), query.metadata.keys())
        if any([self.metadata[k] != query.metadata[k] for k in keys_intersection]):
            return False
        return True

    @property
    def identifier(self):
        return f'{self.name}@{self.version}'
