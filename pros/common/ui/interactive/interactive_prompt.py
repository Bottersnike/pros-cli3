import sys
from typing import *

from .element import Element
from .value_element import ValueElement
from ..basic import _machineoutput
from pros.common import logger, retries


class InteractivePrompt(object):
    def __init__(self, title,
                 description='',
                 abort=False, show_default=True,
                 confirm='OK', cancel='Cancel'):
        self.title = str(title)
        self.description = str(description)
        self.abort = bool(abort)
        self.show_default = bool(show_default)
        self.confirm = str(confirm)
        self.cancel = str(cancel)

    def __call__(self, *args, **kwargs):
        return self.prompt(*args, **kwargs)

    @retries
    def prompt(self, elements: List[Element], can_confirm: bool = True) -> Tuple[bool, Dict[str, Any]]:
        import jsonpickle
        output = {
            'type': 'input/interactive',
            'title': self.title,
            'abort': self.abort,
            'show_default': self.show_default,
            'confirm': self.confirm,
            'cancel': self.cancel,
            'can_confirm': can_confirm,
            'elements': elements
        }
        _machineoutput(output)

        line = sys.stdin.readline()
        result = jsonpickle.decode(line)
        logger(__name__).debug(line.strip(' \n'))
        logger(__name__).debug(result)
        return result.pop('__confirmed'), {
            e.id: e.reconstruct(result[e.id])
            for e in elements
            if isinstance(e, ValueElement)
        }
