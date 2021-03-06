class DispatcherCannotBeNullException(Exception):
    def __init__(self, message):
        super(DispatcherCannotBeNullException, self).__init__(message)


class NoUserAssignedToSession(Exception):
    def __init__(self, message):
        super(NoUserAssignedToSession, self).__init__(message)


class UserNotFound(Exception):
    def __init__(self, message=None):
        self.message = message
        super(UserNotFound, self).__init__(message)


class ModuleNotAvailable(Exception):
    def __init__(self, message=None, module_name=None):
        self.message = message
        self.module_name = module_name
        super(ModuleNotAvailable, self).__init__(message)