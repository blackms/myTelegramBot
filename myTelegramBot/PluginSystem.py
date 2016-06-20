from .Exceptions import DispatcherCannotBeNullException


class BasePlugin(object):
    def __init__(self, *args, **kwargs):
        if 'dispatcher' not in kwargs.keys():
            raise DispatcherCannotBeNullException
        self.dispatcher = kwargs.pop('dispatcher')

    def setup(self):
        raise NotImplemented
