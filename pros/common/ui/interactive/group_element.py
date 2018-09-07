from typing import *

from .element import Element
from .value_element import ValueElement


class GroupElement(ValueElement):
    def __init__(self, id: str, elements: List[Element], title=''):
        super().__init__(id, title=title)
        self.elements = elements

    def reconstruct(self, value: Dict[str, Any]):
        return {
            e.id: e.reconstruct(value[e.id])
            for e in self.elements
            if isinstance(e, ValueElement) and e.id in value.keys()
        }
