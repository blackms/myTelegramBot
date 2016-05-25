class DispatcherCannotBeNullException(Exception):
    def __init__(self, message):
        super(DispatcherCannotBeNullException, self).__init__(message)


class NoUserAssignedToSession(Exception):
    def __init__(self, message):
        super(NoUserAssignedToSession, self).__init__(message)
