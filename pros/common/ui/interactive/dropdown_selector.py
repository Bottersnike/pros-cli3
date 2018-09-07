from .value_element import BasicValueElement


class DropdownSelector(BasicValueElement):
    def __init__(self, id, value, options, title=''):
        super().__init__(id, value, title=title)
        self.options = options
