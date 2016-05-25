from .Exceptions import DispatcherCannotBeNullException


class BasePlugin(object):
    def __init__(self, dispatcher=None):
        assert DispatcherCannotBeNullException, dispatcher is None
        self.dispatcher = dispatcher

    def setup(self):
        raise NotImplemented
