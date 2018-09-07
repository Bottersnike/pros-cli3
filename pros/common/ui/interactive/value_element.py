from .element import Element


class ValueElement(Element):
    def __init__(self, id: str, title=''):
        super().__init__(title)
        self.id = id

    def reconstruct(self, value):
        raise NotImplementedError()


class BasicValueElement(ValueElement):
    def __init__(self, id: str, value, title=''):
        super().__init__(id, title=title)
        self.value = value

    def reconstruct(self, value):
        return value
