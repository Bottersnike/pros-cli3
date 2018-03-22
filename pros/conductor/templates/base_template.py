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
            self.__dict__.update({k: v for k, v in kwargs.pop('orig').__dict__.items() if k in self.__dict__})
        self.__dict__.update({k: v for k, v in kwargs.items() if k in self.__dict__})
        self.metadata.update({k: v for k, v in kwargs.items() if k not in self.__dict__})
        if 'depot' in self.metadata and 'origin' not in self.metadata:
            self.metadata['origin'] = self.metadata.pop('depot')
        if 'd' in self.metadata and 'depot' not in self.metadata:
            self.metadata['depot'] = self.metadata.pop('d')
        if 'l' in self.metadata and 'location' not in self.metadata:
            self.metadata['location'] = self.metadata.pop('l')
        if self.name == 'pros':
            self.name = 'kernel'

    def satisfies(self, query: 'BaseTemplate') -> bool:
        if query.name and self.name != query.name:
            return False
        if query.target and self.target != query.target:
            return False
        if query.version and Version(self.version) not in Spec(query.version):
            return False
        if query.supported_kernels and self.supported_kernels and \
                Version(query.supported_kernels) not in Spec(self.supported_kernels):
            return False
        keys_intersection = set(self.metadata.keys()).intersection(query.metadata.keys())
        # Find the intersection of the keys in the template's metadata with the keys in the query metadata
        # This is what allows us to throw all arguments into the query metadata (from the CLI, e.g. those intended
        # for the depot or template application hints)
        if any([self.metadata[k] != query.metadata[k] for k in keys_intersection]):
            return False
        return True

    def __str__(self):
        fields = [self.metadata.get("origin", None), self.target, self.__class__.__name__]
        additional = ", ".join(map(str, filter(bool, fields)))
        return f'{self.identifier} ({additional})'

    def __gt__(self, other):
        if isinstance(other, BaseTemplate):
            return self.name == other.name and Version(self.version) > Version(other.version)
        else:
            return False

    @property
    def identifier(self):
        return f'{self.name}@{self.version}'

    @classmethod
    def create_query(cls, name: str = None, **kwargs) -> 'BaseTemplate':
        if not isinstance(name, str):
            return cls(**kwargs)
        if name.count('@') > 1:
            raise ValueError(f'Malformed identifier: {name}')
        if '@' in name:
            name, kwargs['version'] = name.split('@')
        return cls(name=name, **kwargs)
