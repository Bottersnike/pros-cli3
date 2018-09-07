class Element(object):
    def __init__(self, title=''):
        self.title = title

    def __getstate__(self):
        return {
            'type': self.__class__.__name__,
            **self.__dict__
        }
